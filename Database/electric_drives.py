E1 = {'name': 'P100T4',        # https://www.saluqimotors.com/products/
      'peakpower': 130,         # kW
      'continiouspower': 100,  #
      'avg_efficiency': .95,    # Motor plus inverter
      'ratedTorque': 220,
      'ratedRPM': 3500,
      'maxRpM': 5000,
      'mass':27,
      'inverter_included': True}

E2 = {'name': 'SIMONTICS_SD_Pro', # https://quickselector.azurewebsites.net/ldp-finder?REGION=WW&LANGUAGE=en&KEEPALIVEURL=https%3A%2F%2Fmall.industry.siemens.com%2Fspice%2Fjom%2Fpolling%2Fpoll&RESULTURL=https%3A%2F%2Fmall.industry.siemens.com%2Fspice%2Fjom%2FController%2Fselector%2FreceiveResul
      'peakpower': 152 ,
      'continiouspower': 132,
      'avg_efficiency': 95.6,
      'ratedTorque': 850,
      'ratedRPM': 1490,
      'maxRpM': 1800,
      'Voltagerange': (400, 690),
      'mass': 960,
      'inverter_included': False}



E3 = {'name': 'SIMOTICS_XP-315L-IM_B3-2p', # https://quickselector.azurewebsites.net/ldp-finder?REGION=WW&LANGUAGE=en&KEEPALIVEURL=https%3A%2F%2Fmall.industry.siemens.com%2Fspice%2Fjom%2Fpolling%2Fpoll&RESULTURL=https%3A%2F%2Fmall.industry.siemens.com%2Fspice%2Fjom%2FController%2Fselector%2FreceiveResul
      'peakpower': 179 ,
      'continiouspower': 160,
      'avg_efficiency': 95.4,
      'ratedTorque': 425,
      'ratedRPM': 3600,
      'maxRpM': 5000,
      'Voltagerange': (400, 690),
      'mass': 1360,
      'inverter_included': False}
#SMG220 OHW
E4= {'name': 'SMG220 OHW',
      'peakpower': 140 ,
      'continiouspower': 120,
      'avg_efficiency': 95,         #Assumed
      'ratedTorque': 200,
      'ratedRPM': 3600,
      'maxRpM': 15500,
      'Voltagerange': (390, 500),
      'mass': 60,
      'inverter_included': False}

Electrical_engines = [E1,E2,E3,E4]
