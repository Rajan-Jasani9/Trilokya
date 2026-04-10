"""
DRDO Technology Foresight catalog (domains from public listing).
Source: https://drdo.gov.in/drdo/en/offerings/technology-foresight

technology_name values are chosen to match Technology.name in the DB where the
project already seeds icons (init_technologies.py); otherwise they match the
foresight page label. Labs are representative DRDO org units — enrich from
programme documents where needed.
"""

# Major DRDO labs / centres (code, display name, org_type)
ORG_UNITS = [
    {"code": "DRDO-HQ", "name": "DRDO Headquarters", "org_type": "Directorate"},
    {"code": "ADA", "name": "Aeronautical Development Agency", "org_type": "Lab"},
    {"code": "ADE", "name": "Aeronautical Development Establishment", "org_type": "Lab"},
    {"code": "ARDE", "name": "Armament Research & Development Establishment", "org_type": "Lab"},
    {"code": "ASL", "name": "Advanced Systems Laboratory", "org_type": "Lab"},
    {"code": "ASTE", "name": "Aeronautical Test Range / ASTE", "org_type": "Lab"},
    {"code": "CAIR", "name": "Centre for Artificial Intelligence & Robotics", "org_type": "Lab"},
    {"code": "CABS", "name": "Centre for Airborne Systems", "org_type": "Lab"},
    {"code": "CASDE", "name": "Centre for Advanced Systems & DE", "org_type": "Lab"},
    {"code": "CHESS", "name": "Centre for High Energy Systems & Sciences", "org_type": "Lab"},
    {"code": "CFEES", "name": "Centre for Fire Explosive & Environment Safety", "org_type": "Lab"},
    {"code": "TBRL", "name": "Terminal Ballistics Research Laboratory", "org_type": "Lab"},
    {"code": "DEAL", "name": "Defence Electronics Applications Laboratory", "org_type": "Lab"},
    {"code": "DEBEL", "name": "Defence Bioengineering & Electromedical Laboratory", "org_type": "Lab"},
    {"code": "DIPAS", "name": "Defence Institute of Physiology & Allied Sciences", "org_type": "Lab"},
    {"code": "DL", "name": "Defence Laboratory", "org_type": "Lab"},
    {"code": "DLJ", "name": "Defence Laboratory Jodhpur", "org_type": "Lab"},
    {"code": "DMRL", "name": "Defence Metallurgical Research Laboratory", "org_type": "Lab"},
    {"code": "DMSRDE", "name": "Defence Materials & Stores Research & Development Establishment", "org_type": "Lab"},
    {"code": "DRDL", "name": "Defence Research & Development Laboratory", "org_type": "Lab"},
    {"code": "GTRE", "name": "Gas Turbine Research Establishment", "org_type": "Lab"},
    {"code": "HEMRL", "name": "High Energy Materials Research Laboratory", "org_type": "Lab"},
    {"code": "INMAS", "name": "Institute of Nuclear Medicine & Allied Sciences", "org_type": "Lab"},
    {"code": "IRDE", "name": "Instruments Research & Development Establishment", "org_type": "Lab"},
    {"code": "ISSA", "name": "Integrated Systems & Solutions Agency", "org_type": "Lab"},
    {"code": "ITTL", "name": "Institute of Technology Management", "org_type": "Lab"},
    {"code": "LASTEC", "name": "Laser Science & Technology Centre", "org_type": "Lab"},
    {"code": "LRDE", "name": "Electronics & Radar Development Establishment", "org_type": "Lab"},
    {"code": "NPOL", "name": "Naval Physical & Oceanographic Laboratory", "org_type": "Lab"},
    {"code": "RCI", "name": "Research Centre Imarat", "org_type": "Lab"},
]

# (technology_name, project_suffix, category, lab_codes, cte_specs)
# cte_specs: list of (cte_code_suffix, cte_title, target_trl)
# Project code: PRJ-TF-{order:03d}

FORESIGHT_PROGRAMMES = [
    ("Additive Manufacturing", "Development programme — additive manufacturing for defence", "Mixed", ["DMRL", "ADA"], [("01", "Powder and feedstock qualification", 6), ("02", "Process control and NDT integration", 5)]),
    ("Aero Structures", "Integrated aero structures development", "Hardware", ["ADA", "ADE"], [("01", "Structural design and analysis", 6), ("02", "Full-scale test and certification", 5)]),
    ("Aerodynamics", "Aerodynamics research and tool-chain maturation", "Mixed", ["ADE", "ASTE"], [("01", "Wind tunnel and CFD correlation", 6), ("02", "Flight-data validation", 5)]),
    ("Aeromechanical Systems", "Aeromechanical systems engineering programme", "Hardware", ["ADE", "GTRE"], [("01", "Rotor/propulsion aero-mechanical integration", 6), ("02", "Health monitoring and loads", 5)]),
    ("Agro Technology for Military Support in High Altitude Areas", "High-altitude agro-tech for military logistics", "Mixed", ["DIPAS", "DLJ"], [("01", "Protected cultivation systems", 5), ("02", "Nutrition and preservation chain", 4)]),
    ("AI/ML Technology", "AI/ML platforms for defence applications", "AI", ["CAIR", "RCI"], [("01", "Model lifecycle and governance", 5), ("02", "Edge deployment and assurance", 5)]),
    ("Alternative Power Plant", "Alternative power plant technology maturation", "Hardware", ["GTRE", "DMRL"], [("01", "System architecture and safety case", 6), ("02", "Qualification tests", 5)]),
    ("Antennas", "Advanced antenna systems programme", "Hardware", ["LRDE", "DEAL"], [("01", "Aperture and feed design", 6), ("02", "EMC and environmental qualification", 5)]),
    ("Armoured & Combat Vehicles", "Armoured vehicle systems development", "Hardware", ["ARDE", "DMRL"], [("01", "Protection and survivability", 6), ("02", "Mobility and automotive integration", 5)]),
    ("Autonomous Systems and Robotics", "Autonomous and robotic platforms programme", "Mixed", ["CAIR", "ASL"], [("01", "Autonomy stack and safety", 6), ("02", "Mission integration", 5)]),
    ("Behavioural Analysis for Soldiers", "Behavioural and cognitive support R&D", "Mixed", ["DIPAS", "DEBEL"], [("01", "Measurement and modelling", 5), ("02", "Training and intervention tools", 4)]),
    ("Bio Defence", "Biological defence systems programme", "Hardware", ["DEBEL", "INMAS"], [("01", "Detection and identification", 6), ("02", "Protection and decontamination", 5)]),
    ("Bio Remediation", "Environmental bio-remediation for defence sites", "Mixed", ["DL", "CFEES"], [("01", "Remediation process design", 5), ("02", "Field validation", 4)]),
    ("Biomedical Engineering & Technologies", "Biomedical devices and soldier health tech", "Hardware", ["DEBEL", "INMAS"], [("01", "Device design and trials", 6), ("02", "Regulatory and safety pathway", 5)]),
    ("C4ISR", "C4ISR architecture and integration programme", "Mixed", ["LRDE", "DEAL"], [("01", "Architecture and interoperability", 6), ("02", "Field trials and hardening", 5)]),
    ("Camouflage Technology", "Signature management and camouflage", "Hardware", ["DLJ", "DMSRDE"], [("01", "Material systems development", 6), ("02", "Signature measurement", 5)]),
    ("CBRN Defence", "CBRN defence equipment and doctrine support", "Hardware", ["CFEES", "DEBEL"], [("01", "Detection and PPE", 6), ("02", "Decontamination systems", 5)]),
    ("Communication", "Strategic and tactical communication systems", "Hardware", ["DEAL", "LRDE"], [("01", "Waveforms and terminals", 6), ("02", "Network security integration", 5)]),
    ("Control Systems", "Control systems for weapons and platforms", "Mixed", ["RCI", "ASL"], [("01", "Guidance and control laws", 6), ("02", "HW/SW integration and V&V", 5)]),
    ("Counter Swarm Technology", "Counter-swarm detection and defeat", "Mixed", ["LRDE", "ADE"], [("01", "Sensor fusion and tracking", 6), ("02", "Effector integration", 5)]),
    ("Cyber, Information & Communication Security", "Cyber and information security programme", "Software", ["CAIR", "DEAL"], [("01", "Zero-trust architecture rollout", 5), ("02", "Continuous monitoring", 5)]),
    ("Decoys", "Expendable decoy and countermeasure systems", "Hardware", ["ARDE", "DRDL"], [("01", "Payload and kinematics", 6), ("02", "Operational testing", 5)]),
    ("Detonics & Mechanisms", "Fuzing and detonics mechanisms", "Hardware", ["ARDE", "HEMRL"], [("01", "Initiation safety", 6), ("02", "Reliability qualification", 5)]),
    ("Diesel Engine", "High-performance diesel propulsion", "Hardware", ["GTRE", "ARDE"], [("01", "Combustion and emissions", 6), ("02", "Durability programme", 5)]),
    ("Electric Power Technology", "Electric power and energy management", "Hardware", ["GTRE", "DMRL"], [("01", "Power electronics stack", 6), ("02", "Thermal and EMI management", 5)]),
    ("Electro Optics", "Electro-optical sensors and laser systems", "Hardware", ["IRDE", "LASTEC"], [("01", "Sensor core development", 6), ("02", "Environmental qualification", 5)]),
    ("Electronic Devices", "Microelectronics and RF devices", "Hardware", ["DEAL", "LRDE"], [("01", "Device characterisation", 6), ("02", "Packaging and reliability", 5)]),
    ("Electronic Warfare", "EW systems development and integration", "Hardware", ["LRDE", "DEAL"], [("01", "EW receiver/exciter chain", 6), ("02", "Platform integration", 5)]),
    ("EM Rail Gun", "Electromagnetic launch technology", "Hardware", ["HEMRL", "ARDE"], [("01", "Pulsed power architecture", 5), ("02", "Barrel and materials", 4)]),
    ("Embedded Systems", "Real-time embedded computing for weapons", "Mixed", ["RCI", "DEAL"], [("01", "Safety-critical firmware", 6), ("02", "Certification evidence", 5)]),
    ("Energy", "Energy storage and conversion for defence", "Hardware", ["DMRL", "HEMRL"], [("01", "Cell and pack engineering", 5), ("02", "Safety and BMS", 5)]),
    ("Environment Protection", "Environmental protection and compliance", "Mixed", ["DL", "CFEES"], [("01", "Monitoring systems", 5), ("02", "Remediation integration", 4)]),
    ("Environmental Testing", "Environmental test infrastructure and methods", "Hardware", ["ASTE", "ADE"], [("01", "Test specifications", 6), ("02", "Correlation with field data", 5)]),
    ("Fire Fighting", "Fire suppression for platforms and facilities", "Hardware", ["CFEES", "ARDE"], [("01", "Agent and delivery systems", 5), ("02", "Certification for platforms", 4)]),
    ("Guidance & Navigation", "Guidance and navigation sensor suite", "Mixed", ["RCI", "ASL"], [("01", "INS/GNSS fusion", 6), ("02", "Redundancy and integrity", 5)]),
    ("Guided Artillery", "Guided artillery munitions programme", "Hardware", ["ARDE", "RCI"], [("01", "Guidance section development", 6), ("02", "Ballistic qualification", 5)]),
    ("Gun Technology", "Large and medium calibre gun systems", "Hardware", ["ARDE", "DMRL"], [("01", "Interior ballistics", 6), ("02", "Recoil and structures", 5)]),
    ("Hardware In Loop Simulation", "HIL simulation infrastructure", "Mixed", ["RCI", "ADE"], [("01", "Plant models and interfaces", 6), ("02", "Scenario libraries", 5)]),
    ("High Performance Computing", "HPC for defence R&D workloads", "Software", ["CAIR", "ISSA"], [("01", "Cluster architecture", 5), ("02", "Workload orchestration", 5)]),
    ("Hydro Structures", "Hydro structures and coastal engineering", "Hardware", ["NPOL", "DMRL"], [("01", "Structural design methods", 5), ("02", "Instrumentation", 4)]),
    ("Hypersonic Technologies", "Hypersonic vehicle technologies", "Hardware", ["DRDL", "ADE"], [("01", "Aero-thermal experiments", 5), ("02", "Materials and TPS", 4)]),
    ("Life Support", "Life support and environmental control", "Hardware", ["DEBEL", "DIPAS"], [("01", "Breathing and thermal systems", 6), ("02", "Human trials and certification", 5)]),
    ("Materials", "Advanced materials and metallurgy", "Hardware", ["DMRL", "DMSRDE"], [("01", "Alloy development", 6), ("02", "Processing scale-up", 5)]),
    ("Military Food Technology", "Operational ration and food tech", "Mixed", ["DIPAS", "DEBEL"], [("01", "Formulation and shelf life", 5), ("02", "Field acceptance trials", 4)]),
    ("Mines & Mines Detection", "Mine systems and detection technology", "Hardware", ["ARDE", "IRDE"], [("01", "Sensor modalities", 6), ("02", "Clearance robotics", 5)]),
    ("Missile Systems", "Guided weapons and missile programmes", "Hardware", ["DRDL", "RCI"], [("01", "Seeker and guidance", 6), ("02", "Propulsion integration", 5)]),
    ("Multi-Barrel Rockets", "Rocket artillery systems", "Hardware", ["ARDE", "HEMRL"], [("01", "Launcher mechanics", 6), ("02", "Ballistic dispersion control", 5)]),
    ("Explosives & Pyrotechnics", "Munition energetics and pyrotechnics", "Hardware", ["HEMRL", "ARDE"], [("01", "Formulation safety", 6), ("02", "Production scale-up", 5)]),
    ("Natural Hazard Management", "Natural hazard early warning and mitigation", "Mixed", ["DEAL", "DL"], [("01", "Sensor networks", 5), ("02", "Decision support", 4)]),
    ("Non Destructive Evaluation", "NDE methods for defence hardware", "Hardware", ["DMRL", "IRDE"], [("01", "Modalities and standards", 6), ("02", "Automation and AI assist", 5)]),
    ("Ocean Profiling", "Oceanographic sensors and profiling", "Hardware", ["NPOL", "DEAL"], [("01", "Sensor payloads", 6), ("02", "Data assimilation", 5)]),
    ("Parachute Technology", "Parachute and aerial delivery systems", "Hardware", ["ARDE", "ADE"], [("01", "Canopy materials", 6), ("02", "Deployment dynamics", 5)]),
    ("Passive Countermeasures", "Passive countermeasure systems", "Hardware", ["DLJ", "LASTEC"], [("01", "Signature materials", 6), ("02", "Dispenser integration", 5)]),
    ("Propulsion Technologies", "Air and missile propulsion", "Hardware", ["GTRE", "DRDL"], [("01", "Combustor development", 6), ("02", "Thrust vectoring", 5)]),
    ("Protective Clothing & Gears", "Protective textiles and PPE", "Hardware", ["DMSRDE", "DEBEL"], [("01", "Material barrier performance", 6), ("02", "Human factors trials", 5)]),
    ("Quantum Technologies", "Quantum sensing and communication R&D", "Mixed", ["LASTEC", "DEAL"], [("01", "Source and detector development", 4), ("02", "Cryogenic and control subsystems", 4)]),
    ("Radar", "Radar systems engineering", "Hardware", ["LRDE", "DEAL"], [("01", "Antenna and exciter", 6), ("02", "Signal processor", 5)]),
    ("Microwave Technologies", "Microwave circuits and subsystems", "Hardware", ["LRDE", "DEAL"], [("01", "MMIC integration", 6), ("02", "Thermal and reliability", 5)]),
    ("Radome", "Radome materials and RF transparency", "Hardware", ["LRDE", "DMRL"], [("01", "Dielectric design", 6), ("02", "Lightning and rain erosion", 5)]),
    ("Respiratory Management", "Respiratory protection and management", "Hardware", ["DEBEL", "INMAS"], [("01", "Filtration performance", 6), ("02", "Ergonomic certification", 5)]),
    ("Seeker", "Precision seeker technology programme", "Hardware", ["IRDE", "RCI"], [("01", "Seeker front-end", 6), ("02", "Tracker algorithms", 5)]),
    ("Sensors/Detectors", "Multi-domain sensors and detectors", "Hardware", ["IRDE", "LRDE"], [("01", "Detector materials", 6), ("02", "Fusion architecture", 5)]),
    ("Soldier Support", "Soldier systems and load carriage", "Hardware", ["ARDE", "DMSRDE"], [("01", "Human factors engineering", 5), ("02", "Power and comms integration", 5)]),
    ("Sonar", "Underwater sonar systems", "Hardware", ["NPOL", "DEAL"], [("01", "Transducer arrays", 6), ("02", "Signal processing", 5)]),
    ("Space Situational Awareness", "SSA sensors and data fusion", "Mixed", ["LRDE", "ISSA"], [("01", "Sensor tasking", 5), ("02", "Catalogue maintenance", 4)]),
    ("Space Technologies", "Space payloads and bus technologies", "Hardware", ["LRDE", "RCI"], [("01", "Payload engineering", 5), ("02", "Environmental testing", 5)]),
    ("Surveillance and Tracking", "Surveillance and target tracking systems", "Hardware", ["LRDE", "IRDE"], [("01", "Sensor suite integration", 6), ("02", "C2 interfaces", 5)]),
    ("Swarm Technology", "Swarm autonomy and coordination", "Mixed", ["CAIR", "ASL"], [("01", "Swarm algorithms", 5), ("02", "Communications mesh", 5)]),
    ("Terahertz", "Terahertz imaging and spectroscopy", "Hardware", ["LASTEC", "IRDE"], [("01", "Sources and detectors", 4), ("02", "System integration", 4)]),
    ("UAV", "Unmanned aerial vehicle programmes", "Mixed", ["ADE", "CAIR"], [("01", "Airframe and propulsion", 6), ("02", "GCS and datalink", 5)]),
    ("UGV", "Unmanned ground vehicle programmes", "Mixed", ["CAIR", "ARDE"], [("01", "Mobility and autonomy", 6), ("02", "Weapon/sensor integration", 5)]),
    ("Underwater Defence Technologies", "Underwater defence systems", "Hardware", ["NPOL", "DRDL"], [("01", "Torpedo subsystems", 6), ("02", "Countermeasure systems", 5)]),
    ("Wargaming", "Wargaming and simulation for operations", "Software", ["ISSA", "ITTL"], [("01", "Scenario engine", 5), ("02", "Analytics and after-action", 4)]),
    ("Warhead/Explosive & Ballistic Protection", "Warhead and ballistic protection", "Hardware", ["HEMRL", "DMRL"], [("01", "Warhead mechanics", 6), ("02", "Armour solutions", 5)]),
    ("Waste Management", "Waste treatment for defence installations", "Mixed", ["CFEES", "DL"], [("01", "Treatment processes", 4), ("02", "Monitoring and compliance", 4)]),
    ("Fibre Optics & Photonics", "Fibre and photonic subsystems", "Hardware", ["DEAL", "LASTEC"], [("01", "Link budget and BER", 6), ("02", "Ruggedised packaging", 5)]),
    ("Flight Sciences", "Flight sciences and flight testing", "Mixed", ["ADE", "ASTE"], [("01", "Flight test instrumentation", 6), ("02", "Data reduction methods", 5)]),
    ("Gas Turbine Engine", "Gas turbine propulsion development", "Hardware", ["GTRE", "ADE"], [("01", "Core and hot section", 6), ("02", "Controls and FADEC", 5)]),
    ("Life Sciences", "Life sciences for human performance", "Mixed", ["DIPAS", "DEBEL"], [("01", "Physiology studies", 5), ("02", "Countermeasure biology", 4)]),
    ("Naval Systems", "Naval platform and combat systems", "Hardware", ["NPOL", "DRDL"], [("01", "Combat management integration", 6), ("02", "Hull signatures", 5)]),
    ("Night Vision Technology", "Night vision and low-light imaging", "Hardware", ["IRDE", "LASTEC"], [("01", "Image intensifier chain", 6), ("02", "Fusion with thermal", 5)]),
    ("Nuclear Technology", "Nuclear science applications for defence", "Hardware", ["INMAS", "HEMRL"], [("01", "Detection instrumentation", 5), ("02", "Safety systems", 5)]),
    ("Simulation & Modelling", "Simulation and digital modelling", "Software", ["ISSA", "ADE"], [("01", "Physics-based models", 5), ("02", "Digital twin workflows", 5)]),
    ("Stealth Technology", "Low-observable and stealth engineering", "Hardware", ["ADE", "LRDE"], [("01", "RCS management", 5), ("02", "Materials and coatings", 5)]),
    ("Textile & Special Materials", "Ballistic textiles and special fabrics", "Hardware", ["DMSRDE", "ARDE"], [("01", "Yarn and weave optimisation", 6), ("02", "Ballistic testing", 5)]),
    ("Underwater Weapons", "Underwater weapon systems", "Hardware", ["NPOL", "DRDL"], [("01", "Propulsion hydrodynamics", 6), ("02", "Guidance in water", 5)]),
]


def build_seed_document() -> dict:
    from datetime import date

    programmes = []
    for i, row in enumerate(FORESIGHT_PROGRAMMES, start=1):
        tech_name, proj_suffix, category, lab_codes, cte_specs = row
        pcode = f"PRJ-TF-{i:03d}"
        tf_part = pcode.replace("PRJ-", "")  # TF-001
        programmes.append(
            {
                "technology_name": tech_name,
                "foresight_source_label": tech_name,
                "project": {
                    "code": pcode,
                    "name": f"{tech_name}: {proj_suffix.split('—')[0].strip()}",
                    "description": proj_suffix,
                    "category": category,
                    "start_date": str(date(2024, 4, 1)),
                    "end_date": None,
                    "org_unit_codes": lab_codes,
                },
                "ctes": [
                    {
                        "code": f"CTE-{tf_part}-{sfx}",
                        "name": title,
                        "description": None,
                        "category": None,
                        "target_trl": trl,
                    }
                    for sfx, title, trl in cte_specs
                ],
            }
        )

    return {
        "meta": {
            "title": "DRDO Technology Foresight seed",
            "source_url": "https://drdo.gov.in/drdo/en/offerings/technology-foresight",
            "notes": (
                "Domains are aligned with the public Technology Foresight listing plus additional "
                "technology rows that match init_technologies.py (e.g. Fibre Optics, Naval Systems). "
                "Project titles and participating labs are representative—not extracted from detail "
                "PDFs on the website. Enrich org_unit_codes and descriptions from official documents."
            ),
            "version": "1.0",
            "generated_for_schema": {
                "org_units": "org_units",
                "technologies": "technologies (resolve by technology_name)",
                "projects": "projects",
                "project_technologies": "project_technologies",
                "project_org_units": "project_org_units",
                "ctes": "ctes",
            },
        },
        "org_units": ORG_UNITS,
        "programmes": programmes,
    }
