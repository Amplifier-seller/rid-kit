# Gromacs command
gmx_prep_cmd = "gmx grompp"
gmx_run_cmd = "gmx mdrun"
gmx_trjconv_cmd = "gmx trjconv"
gmx_traj_cmd = 'echo "0\n" | gmx traj'

mdp_parameters = {
    "md": {
        "ns-type": "Grid", 
        "dt": "0.002", 
        "tau-t": "0.2 0.2", 
        "tau-p": "1.5", 
        "continuation": "no", 
        "wall-r-linpot": "-1", 
        "optimize-fft": "no", 
        "include": "", 
        "nsteps": "50000", 
        "gen-vel": "no", 
        "rotation": "no", 
        "fourier-ny": "0", 
        "fourier-nx": "0", 
        "fourier-nz": "0", 
        "pbc": "xyz", 
        "compressibility": "4.5e-5", 
        "energygrps": "", 
        "constraints": "h-bonds", 
        "pme-order": "4", 
        "nstvout": "500", 
        "energygrp-excl": "", 
        "comm-mode": "Linear", 
        "gen-seed": "173529", 
        "constraint-algorithm": "Lincs", 
        "lincs-warnangle": "30", 
        "Shake-SOR": "no", 
        "nstxtcout": "500", 
        "wall-type": "9-3", 
        "user1-grps": "", 
        "epsilon-surface": "0", 
        "pcoupltype": "Isotropic", 
        "userint4": "0", 
        "tcoupl": "v-rescale", 
        "rlist": "1.2", 
        "userint1": "0", 
        "userint2": "0", 
        "userint3": "0", 
        "tc-grps": "water non-water", 
        "table-extension": "1", 
        "wall-atomtype": "", 
        "nstlist": "10", 
        "shake-tol": "0.0001", 
        "wall-density": "", 
        "rcoulomb": "1.2", 
        "ref-t": "300 300", 
        "ref-p": "1.0", 
        "DispCorr": "no", 
        "integrator": "md", 
        "epsilon-rf": "0", 
        "wall-ewald-zfac": "3", 
        "userreal3": "0", 
        "pcoupl": "parrinello-rahman", 
        "user2-grps": "", 
        "define": "", 
        "vdw-modifier": "force-switch", 
        "simulation-part": "1", 
        "nwall": "0", 
        "nstcomm": "1000", 
        "pull": "no", 
        "init-step": "0", 
        "energygrp-table": "", 
        "cutoff-scheme": "Verlet", 
        "refcoord-scaling": "No", 
        "fourierspacing": "0.15", 
        "userreal4": "0", 
        "userreal2": "0", 
        "gen-temp": "300", 
        "userreal1": "0", 
        "nstxout": "500", 
        "nstlog": "0", 
        "nstenergy": "500", 
        "lincs-order": "4", 
        "ewald-geometry": "3d", 
        "periodic-molecules": "no", 
        "xtc-precision": "1000", 
        "tinit": "0", 
        "vdw-type": "Cut-off", 
        "nstcalcenergy": "10000", 
        "coulombtype": "pme", 
        "morse": "no", 
        "xtc-grps": "", 
        "epsilon-r": "1", 
        "ewald-rtol": "1e-05", 
        "comm-grps": "", 
        "lincs-iter": "1", 
        "nstfout": "500", 
        "rvdw": "1.2",
        "rvdw-switch": "1.0"
    },
    "ions": {
        "emtol": "1000.0", 
        "rlist": "1.2", 
        "nstlist": "10", 
        "integrator": "steep", 
        "coulombtype": "PME", 
        "pbc": "xyz", 
        "rcoulomb": "1.2", 
        "cutoff-scheme": "Verlet", 
        "emstep": "0.01", 
        "ns_type": "grid", 
        "nsteps": "50000", 
        "rvdw": "1.2"
    }
}

