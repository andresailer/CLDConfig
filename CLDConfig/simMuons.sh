#!/bin/bash

parallel -j 2 --results output_sim_base_{} \
ddsim --compactFile $k4geo_DIR/FCCee/CLD/compact/CLD_o2_v07/CLD_o2_v07.xml \
      --steeringFile cld_steer.py \
      --numberOfEvents 10000 \
      --enableGun \
      --gun.particle {} \
      --gun.energy "40*GeV" \
      --gun.thetaMin "89*deg" \
      --gun.thetaMax "89*deg" \
      --gun.distribution "uniform" \
      --runType batch \
      --outputFile sim89_base_stepper_{}.root \
      ::: mu- mu+

parallel -j 2 --results output_sim_new_{} \
ddsim --compactFile $k4geo_DIR/FCCee/CLD/compact/CLD_o2_v07/CLD_o2_v07.xml \
      --steeringFile cld_steer_stepper.py \
      --numberOfEvents 10000 \
      --enableGun \
      --gun.particle {} \
      --gun.energy "40*GeV" \
      --gun.thetaMin "89*deg" \
      --gun.thetaMax "89*deg" \
      --gun.distribution "uniform" \
      --runType batch \
      --outputFile sim89_new_stepper_{}.root \
      ::: mu- mu+

parallel -j 2 --results output_rec_base_{} \
         k4run \
         CLDReconstruction.py \
         --compactFile $k4geo_DIR/FCCee/CLD/compact/CLD_o2_v07/CLD_o2_v07.xml \
         --inputFiles sim89_base_stepper_{}.root \
         --outputBasename rec89_base_stepper_{} \
         --trackingOnly \
         --num-events 10000 \
         ::: mu- mu+ &
parallel -j 2  --results output_rec_new_{} \
         k4run \
         CLDReconstruction.py \
         --compactFile $k4geo_DIR/FCCee/CLD/compact/CLD_o2_v07/CLD_o2_v07.xml \
         --outputBasename rec89_new_stepper_{} \
         --inputFiles sim89_new_stepper_{}.root \
         --trackingOnly \
         --num-events 10000 \
         ::: mu- mu+ &


parallel -j 2 --results output_sim_base_{} \
ddsim --compactFile $k4geo_DIR/FCCee/CLD/compact/CLD_o2_v07/CLD_o2_v07.xml \
      --steeringFile cld_steer.py \
      --numberOfEvents 10000 \
      --enableGun \
      --gun.particle {} \
      --gun.momentumMin "20*GeV" \
      --gun.momentumMax "80*GeV" \
      --gun.thetaMin "89*deg" \
      --gun.thetaMax "89*deg" \
      --gun.distribution "uniform" \
      --runType batch \
      --outputFile sim20_80_base_stepper_{}.root \
      ::: mu- mu+

parallel -j 2  --results output_rec2080_new_{} \
         k4run \
         CLDReconstruction.py \
         --compactFile $k4geo_DIR/FCCee/CLD/compact/CLD_o2_v07/CLD_o2_v07.xml \
         --outputBasename rec_p20-80_stepper_{} \
         --inputFiles sim20_80_base_stepper_{}.root \
         --trackingOnly \
         --num-events 10000 \
         ::: mu- mu+ &


# simulate and reconstruct mixed hepMC file
ddsim --compactFile $k4geo_DIR/FCCee/CLD/compact/CLD_o2_v07/CLD_o2_v07.xml \
      --steeringFile cld_steer.py \
      --numberOfEvents 10000 \
      --inputFiles mu_theta_90_p_20-80.hepmc \
      --runType batch \
      --outputFile sim_hepmc_stepper.root && \
    k4run \
        CLDReconstruction.py \
        --compactFile $k4geo_DIR/FCCee/CLD/compact/CLD_o2_v07/CLD_o2_v07.xml \
        --outputBasename rec_hepmc_stepper \
        --inputFiles sim_hepmc_stepper.root \
        --trackingOnly \
        --num-events 10000
