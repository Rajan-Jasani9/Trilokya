/**
 * Maps backend icon_filename stem (e.g. radar from radar.svg) to bundled PNGs in src/assets.
 */
import additiveManufacturing from '../assets/additive-manufacturing.png'
import aeroStructures from '../assets/aerostructures-.png'
import aerodynamics from '../assets/aerodynamics-.png'
import aeromechanical from '../assets/aeromechanical-.png'
import agroTechnology from '../assets/agro-technology-.png'
import aiMl from '../assets/ai-ml-.png'
import alternativePowerPlant from '../assets/alternative-power-plant-.png'
import antenna from '../assets/antenna.png'
import armouredCombat from '../assets/armoured-and-combat-vehicle-.png'
import autonomousRobotics from '../assets/autonomous-systems-and-robotics-.png'
import behaviouralAnalysis from '../assets/behavioural-analysis-.png'
import bioDefence from '../assets/bio-defence-.png'
import bioRemediation from '../assets/bio-remediation-.png'
import biomedical from '../assets/biomedical-engineering-.png'
import c4isr from '../assets/c4isr-.png'
import camouflage from '../assets/camouflague-.png'
import cbrn from '../assets/cbrn-defence-.png'
import communication from '../assets/communication.png'
import controlSystems from '../assets/control-systems-.png'
import counterSwarm from '../assets/counter-swarm-.png'
import cyber from '../assets/cyber.png'
import decoys from '../assets/decoys-.png'
import detonics from '../assets/detonics-.png'
import dieselEngine from '../assets/diesel-engine-.png'
import electricPower from '../assets/electric-power-.png'
import electroOptics from '../assets/eo-.png'
import electronicDevices from '../assets/electronics-devices-.png'
import electronicWarfare from '../assets/ew-.png'
import emRailGun from '../assets/em-railgun-.png'
import embeddedSystems from '../assets/embedded-systems-.png'
import energy from '../assets/energy-.png'
import environmentProtection from '../assets/environment-protection-.png'
import environmentalTesting from '../assets/environmental-testing-.png'
import fireFighting from '../assets/fire-fighting-.png'
import guidanceNavigation from '../assets/guidance-and-Navigation-.png'
import guidedArtillery from '../assets/guided-artillery-.png'
import gunTechnology from '../assets/gun-technology.png'
import hwInLoop from '../assets/hw-in-loop-simulation-.png'
import hpc from '../assets/hpc-.png'
import hydroStructures from '../assets/hydro-structure-.png'
import hypersonic from '../assets/hypersonic-.png'
import lifeSupport from '../assets/life-support-.png'
import material from '../assets/material-.png'
import militaryFood from '../assets/military-food-.png'
import mines from '../assets/mines-.png'
import missile from '../assets/missile-.png'
import multiBarrelRockets from '../assets/multi-barrel-rockets-.png'
import munition from '../assets/munition-.png'
import naturalHazard from '../assets/natural-hazard.png'
import nonDestructiveEvaluation from '../assets/non-destructive-evaluation.png'
import oceanProfiling from '../assets/ocean-profiling.png'
import parachute from '../assets/parachute.png'
import passiveCountermeasure from '../assets/passive-countermesaure.png'
import propulsion from '../assets/propulsion.png'
import protectiveClothing from '../assets/protective-clothing.png'
import quantum from '../assets/quantum.png'
import radar from '../assets/radar.png'
import radome from '../assets/radome.png'
import respiratoryManagement from '../assets/respiratory-management.png'
import seeker from '../assets/seeker.png'
import sensor from '../assets/sensor.png'
import soldierSupport from '../assets/soldier-support.png'
import sonar from '../assets/sonar.png'
import ssa from '../assets/ssa.png'
import spaceTechnologies from '../assets/space-technologies.png'
import surveillanceTracking from '../assets/surveillanve.png'
import swarm from '../assets/swarm.png'
import terahertz from '../assets/terahertz.png'
import uav from '../assets/uav.png'
import ugv from '../assets/ugv_0.png'
import underwaterDefence from '../assets/underwater-defence.png'
import wargaming from '../assets/wargaming.png'
import warheadProtection from '../assets/warheadexplosiveandballisticprotection-.png'
import wasteManagement from '../assets/waste-managemet.png'

const TECHNOLOGY_IMAGE_BY_SLUG = {
  additive_manufacturing: additiveManufacturing,
  aero_structures: aeroStructures,
  aerodynamics,
  aeromechanical_systems: aeromechanical,
  agro_technology_for_military_support_in_high_altitude_areas: agroTechnology,
  ai_and_ml_technology: aiMl,
  alternative_power_plant: alternativePowerPlant,
  antennas: antenna,
  armoured_and_combat_vehicles: armouredCombat,
  autonomous_systems_and_robotics: autonomousRobotics,
  behavioural_analysis_for_soldiers: behaviouralAnalysis,
  bio_defence: bioDefence,
  bio_remediation: bioRemediation,
  biomedical_engineering_and_technologies: biomedical,
  c4isr,
  camouflage_technology: camouflage,
  cbrn_defence: cbrn,
  communication,
  control_systems: controlSystems,
  counter_swarm_technology: counterSwarm,
  cyber_information_and_communication_security: cyber,
  decoys,
  detonics_and_mechanisms: detonics,
  diesel_engine: dieselEngine,
  electric_power_technology: electricPower,
  electro_optics: electroOptics,
  electronic_devices: electronicDevices,
  electronic_warfare: electronicWarfare,
  em_rail_gun: emRailGun,
  embedded_systems: embeddedSystems,
  energy,
  environment_protection: environmentProtection,
  environmental_testing: environmentalTesting,
  fire_fighting: fireFighting,
  guidance_and_navigation: guidanceNavigation,
  guided_artillery: guidedArtillery,
  gun_technology: gunTechnology,
  hardware_in_loop_simulation: hwInLoop,
  high_performance_computing: hpc,
  hydro_structures: hydroStructures,
  hypersonic_technologies: hypersonic,
  life_support: lifeSupport,
  materials: material,
  military_food_technology: militaryFood,
  mines_and_mines_detection: mines,
  missile_systems: missile,
  multi_barrel_rockets: multiBarrelRockets,
  munition_and_ammunition: munition,
  natural_hazard_management: naturalHazard,
  non_destructive_evaluation: nonDestructiveEvaluation,
  ocean_profiling: oceanProfiling,
  parachute_technology: parachute,
  passive_countermeasures: passiveCountermeasure,
  propulsion_technologies: propulsion,
  protective_clothing_and_gears: protectiveClothing,
  quantum_technologies: quantum,
  radar,
  radome,
  respiratory_management: respiratoryManagement,
  seeker,
  sensors_and_detectors: sensor,
  soldier_support: soldierSupport,
  sonar,
  space_situational_awareness: ssa,
  space_technologies: spaceTechnologies,
  surveillance_and_tracking: surveillanceTracking,
  swarm_technology: swarm,
  terahertz,
  uav,
  ugv,
  underwater_defence_technologies: underwaterDefence,
  wargaming,
  warhead_and_explosive_and_ballistic_protection: warheadProtection,
  waste_management: wasteManagement,
  /* Extended catalogue — reuse nearest PNG until dedicated assets exist */
  fibre_optics_and_photonics: electroOptics,
  flight_sciences: aerodynamics,
  gas_turbine_engine: propulsion,
  life_sciences: lifeSupport,
  naval_systems: sonar,
  night_vision_technology: electroOptics,
  nuclear_technology: quantum,
  simulation_and_modelling: hpc,
  stealth_technology: camouflage,
  textile_and_special_materials: protectiveClothing,
  underwater_weapons: underwaterDefence,
  microwave_technologies: radar,
  explosives_and_pyrotechnics: munition,
}

/**
 * @param {string | null | undefined} iconFilename — e.g. "radar.svg" from API
 * @returns {string | null} Vite-resolved asset URL, or null if unmapped / missing
 */
export function getTechnologyAssetSrc(iconFilename) {
  if (!iconFilename || typeof iconFilename !== 'string') return null
  const slug = iconFilename.replace(/\.[^.]+$/, '')
  return TECHNOLOGY_IMAGE_BY_SLUG[slug] ?? null
}
