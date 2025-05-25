#Lista de parametros que deben convertirse de C a F
PARAMS_TO_CONVERT = ["reg_temp", "sensor1", "sensor2", "sensor3",
                     "sensor4", "sensor5", "change_over", "target",
                     "disch_temp"

                     ]

ROOT_TO_CONVERT = ["status" , "param"]

def celsius_to_fahrenheit(c):
    return round((c * 9/5) + 32, 2)