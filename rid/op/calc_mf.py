from dflow.python import (
    OP,
    OPIO,
    OPIOSign,
    Artifact,
    Parameter
)

from typing import List, Optional, Union, Dict
from pathlib import Path
import numpy as np
from rid.constants import (
        force_out
    )
from rid.common.gromacs.trjconv import generate_coords, generate_forces
from rid.utils import load_txt, set_directory
from rid.tools.estimator import pseudo_inv
from rid.constants import gmx_coord_name, gmx_force_name
import os


class CalcMF(OP):

    """
    Calculate mean force with the results of restrained MD. 
    
    .. math::
        MeanForce = ( Average(CVs) - Initial(CVs) ) * kappa
        
    CalcMF will handle periodic CVs by `angular_mask`. 
    To get the mean value of CVs near equilibrium state under restrained MD, only part of outputs of CV values 
    (the last `tail` part, for example, the last 90% CV values) are used. 
    
    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "conf": Artifact(Path),
                "trr_traj": Artifact(Path,optional=True),
                "task_name": str,
                "plm_out": Artifact(Path),
                "at": Artifact(Path,optional=True),
                "tail": Parameter(float, default=0.9),
                "cv_config": Dict,
                "label_config": Dict
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "forces": Artifact(Path),
                "frame_coords": Artifact(Path,optional=True),
                "frame_forces": Artifact(Path,optional=True)
            }
        )

    @OP.exec_sign_check
    def execute(
        self,
        op_in: OPIO,
    ) -> OPIO:
        r"""Execute the OP.

        Parameters
        ----------
        op_in : dict
            Input dict with components:

                - `task_name`: (`str`) Task name, used to make sub-directory for the task.
                - `plm_out`: (`Artifact(Path)`) Outputs of CV values from restrained MD simulations. 
                    These outputs are generated by PLUMED2.
                - `kappas`: (`List[float]`) Force constants of harmonic restraints.
                - `at`: (`Artifact(Path)`) Files containing initial CV values, or CV centers.
                - `tail`: (`float`) Only the last `tail` of CV values will be used to estimate mean force.

        Returns
        -------
            Output dict with components:

                - `forces`: (`Artifact(Path)`) Files containing mean forces.

        """
        if op_in["label_config"]["method"] == "restrained":
            data = load_txt(op_in["plm_out"])
            data = data[:, 1:]  # removr the first column(time index).
            centers = load_txt(op_in["at"])

            nframes = data.shape[0]
            
            angular_boolean = (np.array(op_in["cv_config"]["angular_mask"], dtype=int) == 1)
            init_angle = data[0][angular_boolean]
            for ii in range(1, nframes):
                current_angle = data[ii][angular_boolean]
                angular_diff = current_angle - init_angle
                current_angle[angular_diff < -np.pi] += 2 * np.pi
                current_angle[angular_diff >= np.pi] -= 2 * np.pi
                data[ii][angular_boolean] = current_angle

            start_f = int(nframes * (1-op_in["tail"]))
            avgins = np.average(data[start_f:, :], axis=0)

            diff = avgins - centers
            angular_diff = diff[angular_boolean]
            angular_diff[angular_diff < -np.pi] += 2 * np.pi
            angular_diff[angular_diff >  np.pi] -= 2 * np.pi
            diff[angular_boolean] = angular_diff
            ff = np.multiply(op_in["label_config"]["kappas"], diff)
            
            task_path = Path(op_in["task_name"])
            task_path.mkdir(exist_ok=True, parents=True)
            np.savetxt(task_path.joinpath(force_out),  np.reshape(ff, [1, -1]), fmt='%.10e')
        elif op_in["label_config"]["method"] == "constrained":
            data = load_txt(op_in["plm_out"])
            data = data[:, 1:]  # removr the first column(time index).
            centers = data[0,:]
            
            generate_coords(trr = op_in["trr_traj"], top = op_in["conf"], out_coord=gmx_coord_name)
            generate_forces(trr = op_in["trr_traj"], top = op_in["conf"], out_force=gmx_force_name)
            # Kb to KJ/mol
            KB = 0.0083148648645
            T = 372.18045
            coords = np.loadtxt(gmx_coord_name,comments=["#","@"])
            # coords units nm
            coords = coords[:,1:]
            forces = np.loadtxt(gmx_force_name,comments=["#","@"])
            # forces units to KJ/(mol*nm)
            forces = forces[:,1:]
            
            mflist = []
            selected_atomid = op_in["cv_config"]["selected_atomid"]
            selected_atoms = list(set([item for sublist in selected_atomid for item in sublist]))
            selected_atomid_simple = []
            for atom_pairs in selected_atomid:
                selected_atomid_simple.append([selected_atoms.index(i) for i in atom_pairs])
            
            # calculate mean force via singular value decomposition(SVD)
            eps = 0.0001
            for index in range(np.shape(coords)[0]):
                coordlist = coords[index]
                forcelist = forces[index]
                r_cv = []
                f_cv = []
                for atom_id in selected_atoms:
                    atom_id -= 1
                    r_cv.append(coordlist[atom_id*3])
                    r_cv.append(coordlist[atom_id*3+1])
                    r_cv.append(coordlist[atom_id*3+2])
                    f_cv.append(forcelist[atom_id*3])
                    f_cv.append(forcelist[atom_id*3+1])
                    f_cv.append(forcelist[atom_id*3+2])
                B = pseudo_inv(r_cv, centers, selected_atomid_simple)
                # print(B.shape)
                dBdx = []
                for index in range(len(r_cv)):
                    r1 = r_cv.copy()
                    r1[index] += eps
                    B1 = pseudo_inv(r1,centers,selected_atomid_simple)
                    r2 = r_cv.copy()
                    r2[index] -= eps
                    B2 = pseudo_inv(r2, centers,selected_atomid_simple)
                    dBdx.append((B1-B2)/(2*eps))
                dBdx = np.array(dBdx)
                mf = np.matmul(B,f_cv) + KB*T*np.trace(dBdx, axis1=0, axis2=2)
                
                mflist.append(mf)
            
            mflist = np.array(mflist)
            nframes = np.shape(coords)[0]            
            
            start_f = int(nframes * (1-op_in["tail"]))
            avg_force = np.average(mflist[start_f:, :], axis=0)
                
            # std_force = np.std(mf_block, axis = 0)
            task_path = Path(op_in["task_name"])
            task_path.mkdir(exist_ok=True, parents=True)
            np.savetxt(task_path.joinpath(force_out),  np.reshape(avg_force, [1, -1]), fmt='%.10e')
            np.savetxt(task_path.joinpath(gmx_coord_name), coords, fmt='%.10e')
            np.savetxt(task_path.joinpath(gmx_force_name), forces, fmt='%.10e')

        frame_coords = None
        frame_forces = None
        if os.path.exists(task_path.joinpath(gmx_coord_name)):
            frame_coords = task_path.joinpath(gmx_coord_name)
        if os.path.exists(task_path.joinpath(gmx_force_name)):
            frame_forces = task_path.joinpath(gmx_force_name)
            
        op_out = OPIO(
            {
                "forces": task_path.joinpath(force_out),
                "frame_coords": frame_coords,
                "frame_forces": frame_forces
            }
        )
        return op_out
