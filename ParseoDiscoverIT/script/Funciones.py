import re
import os
import shutil
import traceback
import napalm
import yaml
import main


"""if isinstance(switchDiccionario['Modelo'],list): #en caso de que sea modulo
        print('@@@@@@@@@@@@@@@@@@@@@@@@ MODULOS INFORMACIÓN PIEZAS @@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        power_supply_data, cantidad = power_supply_cardsCisco(device)
        fan = fan_cardsCisco(device) # se modifico el return
        power_supply_cardsCisco(device)
        cardsCisco(device) #mafer
        #tarjetas_cisco(device) #vic
        host = encontrar_hostname(device)
        print(f'Este es el HostName: {host}')
    else: #en caso que sea un switch 
    chasisString,switchDiccionario = chasisCisco(device)
    """

def main(output_file):
    print(f'===+++DiscoverIT+++===\n\n')
    device = abrir_archivo(output_file)
    print(f'@@@@@@@@@@@@@@@@@@@@@@@@ CISCO @@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    chasisString,switchDiccionario = chasisCisco(device)
    print(chasisString)
    moduloOrSwitch = re.findall('[S|s][A-Za-z]{2,2}-',device)
    if moduloOrSwitch:
        print(f'\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ MODULAR @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        powerSupply,cantidadPowerSupply = power_supply_cardsCisco(switchDiccionario['Modelo'],device)
        powerString,powerDiccionario=formato_power_supply(powerSupply,cantidadPowerSupply,switchDiccionario['Modelo'])
        print(powerString)
        
        
        ventiladores,cantidadFan = ventiladoresCisco(device,switchDiccionario['Modelo'])
        if not ventiladores:
            ventiladores,cantidad = ventiladores_cisco(device,switchDiccionario['Modelo'])
            fanString,fanDiccionario = formato_fan(ventiladores,cantidad,switchDiccionario['Modelo'])
            print(fanString)
        else: 
            fanString,fanDiccionario = formato_ventiladores(ventiladores,cantidadFan,switchDiccionario['Modelo'])
            print(fanString)
        
        
        cards,cantidadCards = cardsCisco(device)
        cardsString, cardsDiccionario = formato_cards(cards,cantidadCards,switchDiccionario['Modelo'])
        #print(cardsString) 
        
        modulos,cantidadModulo = subModulosCisco(device,switchDiccionario['Modelo'])
        moduloString, moduloDiccionario = formato_sub(modulos,cantidadModulo,switchDiccionario['Modelo'])
        #print(moduloString)
        
        modString = cardsString + '\n' + moduloString
        
        documentacionEquiposParseo(switchDiccionario,chasisString,powerString,fanString,modString,output_file) 
    else:   
        Switch = re.findall('(N5K|N7K|N9K)',device)
        switchN2K = re.findall('N2K',device)
        if Switch:
            print(f'\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ SWITCH INFORMACIÓN PIEZAS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')   
            powerSupply,cantidadPowerSupply = power_Supply(switchDiccionario['Modelo'],device)
            powerString,powerDiccionario=formato_power_supply(powerSupply,cantidadPowerSupply,switchDiccionario['Modelo'])
            print(powerString)
            ventiladores,cantidadFan = ventiladoresCisco(device,switchDiccionario['Modelo'])
            fanString,fanDiccionario = formato_ventiladores(ventiladores,cantidadFan,switchDiccionario['Modelo'])
            print(fanString)
            modulos,cantidadModulo = modulosCisco(device,switchDiccionario['Modelo'])
            moduloString, moduloDiccionario = formato_modulos(modulos,cantidadModulo,switchDiccionario['Modelo'])
            print(moduloString)
            documentacionEquiposParseo(switchDiccionario,chasisString,powerString,fanString,moduloString,output_file) 
            if switchN2K:    
                    switchn2k(device,switchDiccionario['Version del firmware'],switchDiccionario['Hostname'])   
        else:
            print(f'\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ SWITCH INFORMACIÓN PIEZAS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')   
            powerSupply,cantidadPowerSupply=obtener_cisco_power_supply(switchDiccionario['Modelo'],device)
            powerString,powerDiccionario=formato_power_supply(powerSupply,cantidadPowerSupply,switchDiccionario['Modelo'])
            print(powerString)
            ventiladores,cantidad = ventiladores_cisco(device,switchDiccionario['Modelo'])
            fanString,fanDiccionario = formato_fan(ventiladores,cantidad,switchDiccionario['Modelo'])
            print(fanString)
            modulos,cantidadModulo = modulosCisco(device,switchDiccionario['Modelo'])
            moduloString, moduloDiccionario = formato_modulos(modulos,cantidadModulo,switchDiccionario['Modelo'])
            print(moduloString)
            documentacionEquiposParseo(switchDiccionario,chasisString,powerString,fanString,moduloString,output_file)          
                
                
            
     
"""
las funciones conexion y execute_comandos realizan la conexion de los equipos
por medio de ssh y realizan la extracion de la salida de comandos en un archivo.txt
"""   

def conexion(archivo):
    try:
        with open(archivo) as config_file:
            config = yaml.safe_load(config_file)

        device_config = config.get('device', {})
        commands_config = config.get('commands', {})
        driver = napalm.get_network_driver("ios")
        device = driver(**device_config)

        print("Opening device")
        device.open()
        print("Device connected")
        #device.cli(['skip-page-display'])  #no funciona en modular cisco
        return device_config, commands_config, device
    except FileNotFoundError: # cuando no encuentra un archivo
        print(f"Error: File '{archivo}' not found.")
    except yaml.YAMLError as e: # error en el archivo YAML
        print(f"Error occurred while parsing YAML: {str(e)}")
    except Exception as e: # cuando sucede un error en la conexion
        print(f"\n\n############Error occurred in the connection try conected in cisco config #########\n\n\n")
        with open(archivo) as config_file:
            config = yaml.safe_load(config_file)

        device_config = config.get('device', {})
        commands_config = config.get('commands', {})

        print(f'Configuración del dispositivo: {device_config}')
        print(f'Comandos del dispositivo: {commands_config}')

        driver = napalm.get_network_driver("ios")
        device = driver(**device_config)

        print("Opening device")
        device.open()
        print("Device connected")
        #device.cli(['skip-page-display']) # Importante
        return device_config, commands_config, device

def execute_commands(device, commands_config):
    try:
        results = {}
        # Ejecutar los comandos y guardar los resultados
        for command_name, command_value in commands_config.items():
            command_output = device.cli([command_value])
            cadena = command_output[command_value]
            results[command_name] = cadena

        # Guardar los resultados en un archivo de texto
        with open('output.txt', 'w') as output_file:
            for command_name, result in results.items():
                output_file.write(f"Command: {command_name}\n")
                output_file.write(f"Result:\n{result}\n\n")
        print('######################### COMANDOS GUARDADOS EN EL ARCHIVO output.txt #########################')

    except Exception as e:
        print(f"Error ocurrido en main: {str(e)}")
        traceback.print_exc()


"""
La funcion abrir_archivo se utiliza para abrir el archivo de salida de comandos para que con
la funcion de documentacionEquiposParseo se obtenga la informacion para la creacion de la carpeta

""" 
def abrir_archivo(archivo):
    with open(archivo, 'r') as archivo:
        contenido = archivo.read()
    return contenido
 
def documentacionEquiposParseo(switchDiccionario,infoChasis,powerString,fanString,moduloString,output_file):
        print(f'################################## CREACIÓN DE LA CARPETA ##################################')
        if (switchDiccionario['Modelo']) == 'sin modelo' or switchDiccionario['Numero de serie'] == 'sin numero de serie':
            print("\nNO SE PUEDE CREAR LA CARPETA PORQUE NO SE ENCONTRO EL MODELO\n")
        else:
            extension = '.txt'
            archivo_nombre = f"{switchDiccionario['Modelo']}- {switchDiccionario['Numero de serie']}{extension}"
            nombre_carpeta = archivo_nombre.split('.')
            print(f'\nSe guardaron los datos con el nombre: {archivo_nombre}')
            carpeta = switchDiccionario['Marca'] + "-" + nombre_carpeta[0]
            crear_carpeta(carpeta)
            print(f'Nombre de la carpeta: {carpeta}')
                
            insertar('+++PARSEO+++', infoChasis,powerString,fanString,moduloString, archivo_nombre,carpeta)
            insertar_output(output_file,carpeta)
            print("\n ")


"""
La funcion crear_carpeta , crea la carpeta , por medio de la marca, modelo y numero de serie
del equipo para que las funciones insertar_output e insertar, añadan los documentos de la salida 
de comandos y el parseo en la carpeta correspondiente al equipo.

""" 
 
def crear_carpeta(nombre):
# Se define el nombre de la carpeta o directorio a crear
    tipo = type(nombre)
    ruta_actual = os.getcwd()
    directorio = f'{ruta_actual}/equipos/' + nombre 
    print(f' esta creando directorios: {directorio}')
    try:
        os.mkdir(directorio)
    except OSError:
        print("La creación del directorio %s falló" % directorio)
    else:
        print("Se ha creado el directorio: %s " % directorio)

def insertar(parse,infoChasis, infoPower,infoFan, infoModulo, archivo, carpeta):
    

    try:
        # Solo guarda en el archivo la cadena ingresada
        ruta = 'equipos/' + carpeta + '/' + archivo
        print(ruta) 
        with open(ruta, 'w') as archivo:
            concat = parse + ':\n' + infoChasis + '\n\n' + infoPower + '\n' + infoFan + '\n' + infoModulo + '\n'
            archivo.write(str(concat))
            archivo.write('\n')
    except Exception as e:
        print(f"Ocurrió un error al intentar escribir en el archivo: {e}")

def insertar_output(output_file,carpeta):
    ruta = 'equipos/'+carpeta+'/'+output_file
    try:  
        shutil.copy(output_file,ruta)
    except Exception as e:
        print(f"Error ocurrido en main: {str(e)}")
        traceback.print_exc()


"""
las funciones versionFwCisco, modeloCisco, partNumberCisco, serialNumberCisco, chasisCisco,
encontrar_hostname son para encontrar la informacion de los equipos Switch.

"""

def versionFwCisco(output):
    try:
        """   
        Expresión regular para modelos ASR1001, WS-C2960G-24TC-L, WS-C3560X, WS-C3750-48T-E, WS-C4948, WS-C65509-E
    
        Cisco IOS Software, ASR1000 Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), 
        Version 15.4(3)S4
        
        ER: Version\s(\d+\.\d+\(\d+\)[A-Za-z0-9]+)\  
        """
        
        """
        Expresión regular par modelos WS-C3650-48TQ Y 24TS
        
        Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), 
        Version 03.03.04SE
        
        ER: Version\s(\d+\.\d+\.[A-Za-z0-9]+)\s
        """
        
        """
        Expresión regular par modelos N5K,N9K
        
        System version: 5.2(1)N1(8a)      N5K
        
        System version: 7.0(3)I4(1)       N9K
        
        ER: version:\s(\d+\.\d+\(\d+\)[A-Za-z0-9]+\([A-Za-z0-9]+\))
        """
        
        
        """
        Expresión regular par modelos N7K
        
        system:    version 6.2(14)
        
        "system:\s+.+(\d+\.\d+\(\d+\))"
        """
        
        expresionesVersion = ("Version\s(\d+\.\d+\(\d+\)[A-Za-z0-9]+)\,",
                              "Version\s(\d+\.\d+\.[A-Za-z0-9]+)\s",
                              "version:\s(\d+\.\d+\(\d+\)[A-Za-z0-9]+\([A-Za-z0-9]+\))",
                              "system:\s+.+(\d+\.\d+\(\d+\))"
                              )
        
        for expresion in expresionesVersion:
            patter = re.findall(expresion, output)
            if patter:
                version = patter[0]
                break
        
        
        if not version:
            version = "Sin  version"
       
        return version
        
    
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0

def modeloCisco(output):
    try:    
        """
        Encuentra el modelo
        Model Number : WS-C3650-48TQ   
        ER:Model.+\s([A-Za-z]{2,2}\-[A-Za-z0-9]+\-[A-Za-z0-9]+)\s
        """                
            
        """
        Encuentra el modelo
        Product Number = WS-C4948-10GE
        ER:Product Number = ([A-Za-z]{2,2}\-[A-Za-z0-9]+\-[A-Za-z0-9]+)
        """
        
        """
        Encuentra el modelo
        Product Number = 'WS-C6509-E'
        ER:Product Number = '([A-Za-z]{2,2}\-[A-Za-z0-9]+\-[A-Za-z0-9]+)'
        """   
             
                
        """
        Encuentra el modelo
        Chassis Type : WS-C4948
        ER:Chassis Type : ([A-Za-z]{2,2}\-[A-Za-z0-9]+)
        """
       
                
         
        expresionesModelo = ("Product Number = ([A-Za-z]{2,2}\-[A-Za-z0-9]+\-[A-Za-z0-9]+)",
                             "[C|c][A-Za-z]{4,4}\s+([A-Za-z]{2,2}\-[A-Za-z0-9]+\-[A-Za-z0-9]+)",
                             "Model.+\s([A-Za-z]{2,2}\-[A-Za-z0-9]+\-[A-Za-z0-9]+)\s",
                             "Chassis Type : ([A-Za-z]{2,2}\-[A-Za-z0-9]+)"
                            )
            
        for expresion in expresionesModelo:
            patter = re.findall(expresion, output)
            if patter:
                modelo = patter[0]
                break
            else:
                modelo = "sin modelo"
        
        
        return modelo
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0

def partNumberCisco(output,modelo):
    try:
        
        """
        Encuentra el numero de parte
        Part Number = 73-9344-13
                
        ER:Part Number = ([-0-9]+)
        """
        
        expresionesPart = ("Part Number = ([-0-9]+)")
        patter = re.findall(expresionesPart, output)
        if patter:
            partNumber = patter[0]
        else:
            partNumber = modelo
            if not modelo or modelo == 'sin modelo':
                partNumber = "sin número de parte"
        
        return partNumber
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0

def serialNumberCisco(output):
    try:
        
        """
        Encuentra el numero de serie
        Serial Number = FOX1447GSNZ
            
        ER:Serial Number = ([A-Za-z0-9]+)
        """
        
        """
        Encuentra el numero de serie
        Serial Number = 'SNI1824CE4R'
        
        ER:Serial Number = '([A-Za-z0-9]+)'
        """
        
        expresionesSerial = ("Serial Number = ([A-Za-z0-9]+)",
                             "Serial Number = '([A-Za-z0-9]+)'"
                            )
            
        for expresion in expresionesSerial:
            patter = re.findall(expresion, output)
            if patter:
                serialNumber = patter[0]
                break
            else:
                serialNumber = "sin numero de serie"
        
        return serialNumber
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0

def encontrar_hostname(output): 
    
    try:
        expresionesHost = ("hostname\s+(.*)",
                             "([A-Za-z0-9-]+)#"
                            )
            
        for expresion in expresionesHost:
            patter = re.findall(expresion, output)
            if patter:
                hostname = patter[0]
                break
            else:
                hostname = "sin hostname"
        
        return hostname
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0
        

    """   
    def encontrar_hostname(salida):
        # Utiliza una expresión regular para encontrar el nombre de host
        regex_hostname = r"hostname\s+(.*)"
        match = re.search(regex_hostname, salida)
    
     if match:
            # Si se encuentra un nombre de host, devuélvelo
            return match.group(1)
     else:
            # Si no se encuentra un nombre de host, devuelve None o un valor predeterminado según tu preferencia
            return None
    """

def chasisCisco(output):
    try:
               
        """            
        Encuentra el modelo, numero de parte, numero de serie.
    
        NAME: "Chassis", DESCR: "Cisco ASR1001 Chassis w/o IDC"
        PID: ASR1001           , VID: V03, SN: SSI17340A6X
        """
        
        pattern = r'NAME:.+[A-Z0-9-].+\sPID:\s+(([A-Z0-9-]+|\s+)\s).+SN:\s([A-Z0-9-]+|\s+)\s'
        matches = re.findall(pattern,output) 
        
        if matches:
            chasis = matches[0]
            modelo = chasis[0]
            partNumber = chasis[1]
            serialNumber = chasis[2]
            
            if modelo == '  ' or not modelo:
                modelo = modeloCisco(output)
                partNumber = partNumberCisco(output,modelo)
            
        else:
            modelo = modeloCisco(output)
            partNumber = partNumberCisco(output,modelo)
            serialNumber = serialNumberCisco(output)
        
        marca = 'Cisco'
        version = versionFwCisco(output)
        
         
        chasisString,switchDiccionario = formato_chasis_cisco(marca,modelo,serialNumber,partNumber,version,output)
        
        return chasisString,switchDiccionario
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0

def formato_chasis_cisco(marca,modelo,serialNumber,partNumber,version,device):
    try:

        """ 
        Construir el string con la información de cada power supply con el formato 
        Cantidad de power supply: 2
        Informacion power supply 2
        Modulo: Power Supply Module 1
        Descripcion: Cisco ASR1001 AC Power Supply
        Numero de parte: ASR1001-PWR-AC
        Numero de serie: MP51734003G
        """
        
        host = encontrar_hostname(device)
        chasisString = f'\nModelo: {modelo}\nNumero de serie: {serialNumber}\nNumero de parte: {partNumber}\nVersion: {version}\nHostname: {host}'
        
        # Crear el diccionario con la informacion obtenida de cada power supply
        switchDiccionario = {
                            "Marca": marca,
                            "Modelo": modelo,
                            "Numero de serie": serialNumber,
                            "Numero de parte": partNumber,
                            "Version del firmware": version,
                            "Hostname": host
                            }
     
        return chasisString,switchDiccionario
    except Exception as e:
        return {"Error": f"Error al procesar la información de las power supply: {str(e)}"}


"""
Las siguientes funciones obtener_cisco_power_supply, formato_power_supply sacan la informacion de los power 
supply que se encuentran en un Switch.

"""

def formato_power_supply(power_supply_info,cantidad_power_supply,modelo):
    print(f'#################################### POWER SUPPLY ####################################')        
    try:
        if modelo == 'WS-C4948-10GE':
            powerString = f"Cantidad de power supply: {cantidad_power_supply}\n\n"
            for i, power_info in enumerate(power_supply_info, 1):
                powerString += f"Informacion power supply {i}\n"
                powerString += f"ID: {power_info['Modulo']}{i}\n"
                powerString += f"Modelo: {power_info['Product Number']}\n"
                powerString += f"PID: {power_info['Numero de parte']}\n" 
                powerString += f"Numero de serie: {power_info['Numero de serie']}\n\n"
        elif modelo == 'WS-C6509-E':
            powerString = f"Cantidad de power supply: {cantidad_power_supply}\n\n"
            for i, power_info in enumerate(power_supply_info, 1):
                powerString += f"Informacion power supply {i}\n"
                powerString += f"ID: {power_info['Modulo']}\n"
                powerString += f"Descripcion: {power_info['Descripcion']}\n"
                powerString += f"Modelo: {power_info['Numero de parte']}\n" 
                powerString += f"PID: {power_info['Product Number']}\n"
                powerString += f"Numero de serie: {power_info['Numero de serie']}\n\n"
                
            
        else:
            """ 
            Construir el string con la información de cada power supply con el formato 
            Cantidad de power supply: 2
            Informacion power supply 2
            Modulo: Power Supply Module 1
            Descripcion: Cisco ASR1001 AC Power Supply
            Numero de parte: ASR1001-PWR-AC
            Numero de serie: MP51734003G
            """
                
            powerString = f"Cantidad de power supply: {cantidad_power_supply}\n\n"
            for i, power_info in enumerate(power_supply_info, 1):
                powerString += f"Informacion power supply {i}\n"
                powerString += f"ID: {power_info['Modulo']}\n"
                powerString += f"Descripcion: {power_info['Descripcion']}\n"
                powerString += f"PID: {power_info['Numero de parte']}\n" 
                powerString += f"Numero de serie: {power_info['Numero de serie']}\n\n"
            
            
        # Crear el diccionario con la informacion obtenida de cada power supply
        powerDiccionario = {
            'Cantidad de power supply': cantidad_power_supply,
            'Informacion power supply': power_supply_info
        }
        
        

        return powerString,powerDiccionario
    except Exception as e:
        return {"Error": f"Error al procesar la información de las power supply: {str(e)}"}

def obtener_cisco_power_supply(modelo,output):
    try:
        # Utilizamos expresiones regulares para buscar información relevante
        
        expresionesPower = ('([A-Za-z0-9-]{5,5}\s[A-Za-z0-9-]{6,6}\s[A-Za-z0-9-]{6,6}\s.+)\"\,\sDESCR:\s+\"(.+)\"\sPID:\s+(([A-Z0-9-]+|\s+)\s).+SN:\s([A-Z0-9-]+|\s+)\s',
                            '([A-Za-z0-9-]{5,5}\s[A-Za-z0-9-]{6,6}\s.+)\"\,\s+DESCR:\s+\"(.+)\"\sPID:\s+(([A-Z0-9-]+|\s+)\s).+SN:\s([A-Z0-9-]+|\s+)\s',
                            '([A-Za-z]{4,4}\s\d+.+)\"\,\s+DESCR:\s+\"(.+\sPower\s.+)\"\sPID:\s+(([A-Z0-9-\.]+|\s+)\s).+SN:\s([A-Z0-9-]+|\s+)\s'
                            )
        
        for expresion in expresionesPower:
            matches = re.findall(expresion, output)
            if matches:
                # Creamos una lista de diccionarios para almacenar la información de cada suministro de energía
                power_supply_info = []
                for match in matches:
                    modulo = match[0]
                    descripcion = match[1]
                    pid = match[3]
                    sn = match[4]
                    
                    power_info = {
                        "Modulo": modulo,
                        "Descripcion":descripcion,
                        "Numero de parte": pid,
                        "Numero de serie": sn
                    }
                    
                    power_supply_info.append(power_info)
                break
            elif modelo == 'WS-C4948-10GE':        
                inicioExp = '(Power Supply\s)\d+\sIdprom\s:'
                product = 'Product\sNumber\s=\s([A-Za-z0-9-]+)'
                serial = 'Serial\sNumber\s=\s([A-Za-z0-9-]+)'
                partNumber = 'Part\sNumber\s=\s([A-Za-z0-9-]+)'
                
                patter = f'{inicioExp}(\s.+\s)+\s{product}\s+{serial}\s+{partNumber}'
                matches = re.findall(patter, output)
                if matches:
                    # Creamos una lista de diccionarios para almacenar la información de cada suministro de energía
                    power_supply_info = []
                    for match in matches:
                        modulo = match[0]
                        productNumber = match[2]
                        sn = match[3]
                        partNumber = match[4]
                        
                        power_info = {
                            "Modulo": modulo,
                            "Product Number": productNumber,
                            "Numero de parte": partNumber,
                            "Numero de serie": sn
                        }
                        
                        power_supply_info.append(power_info)
                    break

            else:
                power_supply_info = []
                cantidad_power_supply = 0  
                
        #las siguientes lineas de codigo son para quitar los elementos repetidos en un diccionario        
        dic_sin_repetir=[]
        for i in power_supply_info:
            if i not in dic_sin_repetir:
                dic_sin_repetir.append(i) 
        
        # Contamos la cantidad de power supply
        cantidad_power_supply = len(dic_sin_repetir)
                
        return dic_sin_repetir,cantidad_power_supply
                
                
        
    except Exception as e:
        return {"Error": f"Error al procesar la informacion de las power supply {str(e)}"}
   

"""
Las siguientes funciones ventiladores_cisco sacan la informacion de los FAN que se encuentran en 
un Switch.

"""
 
def formato_fan(fan_info,cantidad_fan,modelo):
    print(f'#################################### FAN ####################################')
    try:
        fanString = f"Cantidad de ventiladores es {cantidad_fan} en el equipo {modelo}\n\n"
        for i, fan_info in enumerate(fan_info, 1):
            fanString += f"Informacion ventilador {i}\n"
            fanString += f"ID: {fan_info['Modulo']}\n"
            fanString += f"Modelo: {fan_info['Modelo']}\n\n"
            
            
        # Crear el diccionario con la informacion obtenida de cada power supply
        fanDiccionario = {
            'Cantidad de ventiladores': cantidad_fan,
            'Informacion ventiladores': fan_info
        }

        return fanString,fanDiccionario
    except Exception as e:
        return {"Error": f"Error al procesar la información de las power supply: {str(e)}"}

def ventiladores_cisco(output,modelo):
    try:
        # Utilizamos expresiones regulares para buscar información relevante
        
        expresionesFan = ('([A-Z][A-Za-z]{2,2}\s+\d+\/\d+)\"',
                          '([A-Z][A-Za-z]{2,2}\s+\d+)\"',
                          '\d\s+([A-Z][A-Za-z]{2,2}\s+\d+)\s'
                          )
        
        expresionModuloFan = ('([F|f][A-Za-z]{2,2}\s+[A-Za-z]{4,4})\"',
                              '[F|f][A-Za-z]{2,2}-[A-Za-z]{4,4}\s\d',
                              '([S|s][A-Za-z]{3,3}\s+\d+)\",.+\((\d+\s[S|s][A-Za-z]{3,3}).+([F|f][A-Za-z]{2,2}\s+[A-Za-z]{6,6})\"'
                             )


        for expresionModulos in expresionModuloFan: 
            matchesModulo = re.findall(expresionModulos,output)
            if matchesModulo:
                ventiladores = []
                for matchesM in matchesModulo:
                    modulo = matchesM
                    fan_info = {
                        "Modulo": modulo,
                        "Modelo": modelo
                    }
                    ventiladores.append(fan_info)
                ventiladores.append(fan_info)
                dic_sin_repetir=[]
                for i in ventiladores: 
                    if i not in dic_sin_repetir:
                        dic_sin_repetir.append(i)
                        
                cantidad_fan = len(dic_sin_repetir)
                break 
                
        for expresion in expresionesFan:
            matches = re.findall(expresion, output)
            if matches and not matchesModulo:
                ventiladores = []
                for match in matches:
                    modulo = match 
                    fan_info = {
                        "Modulo": modulo,
                        "Modelo": modelo
                    }
                    ventiladores.append(fan_info)
                    dic_sin_repetir=[]
                    for i in ventiladores: 
                        if i not in dic_sin_repetir:
                            dic_sin_repetir.append(i)
                        
                    cantidad_fan = len(dic_sin_repetir)  
                break
            

        if not matches and not matchesModulo:
            dic_sin_repetir = []
            cantidad_fan = 0
        
        return dic_sin_repetir,cantidad_fan
        
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0
    

"""
Las siguientes funciones sacan la informacion de las power supply y ventiladores de 
los equipos N7K,N5K, N9K
"""      

def power_Supply(modelo,output):
    
    try:
        print(f'#################################### POWER SUPPLY ####################################')
        # Utilizamos expresiones regulares para buscar información relevante
        
        expresionesPower = ('\"([A-Za-z0-9-]{5,5}\s[A-Za-z0-9-]{6,6}\s\d+)\"\,\s+DESCR:\s+\"(.+)\"\sPID:\s+(([A-Z0-9-]+|\s+)\s).+SN:\s([A-Z0-9-]+|\s+)\s',
                            '\"([A-Za-z0-9-]{4,4}\s\d+)\"\,\s+DESCR:\s+\"(.+[P|p][A-Za-z]{4,4}\s+[S|s][A-Za-z]{5,5})\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s'
                            )
        
        for expresion in expresionesPower:
            matches = re.findall(expresion, output)
            if matches:
                # Creamos una lista de diccionarios para almacenar la información de cada suministro de energía
                power_supply_info = []
                for match in matches:
                    modulo = match[0]
                    descripcion = match[1]
                    pid = match[3]
                    sn = match[4]
                    
                    power_info = { 
                        "Modulo": modulo,
                        "Descripcion":descripcion,
                        "Numero de parte": pid,
                        "Numero de serie": sn
                    }
                    
                    power_supply_info.append(power_info)
                break
            else:
                power_supply_info = []
                cantidad_power_supply = 0  
                
                
        #las siguientes lineas de codigo son para quitar los elementos repetidos en un diccionario        
        dic_sin_repetir=[]
        for i in power_supply_info:
            if i not in dic_sin_repetir:
                dic_sin_repetir.append(i) 
        
        # Contamos la cantidad de power supply
        cantidad_power_supply = len(dic_sin_repetir)

        return dic_sin_repetir,cantidad_power_supply
    except Exception as e:
        return {"Error": f"Error al procesar la informacion de las power supply {str(e)}"}
    
def formato_ventiladores(fan_info,cantidad_fan,modelo):
    print(f'#################################### FAN ####################################')
    try:
        fanString = f"Cantidad de ventiladores es {cantidad_fan} en el equipo {modelo}\n\n"
        for i, fan_info in enumerate(fan_info, 1):
            fanString += f"Informacion ventilador {i}\n"
            fanString += f"ID: {fan_info['Modulo']}\n"
            fanString += f"Modelo: {fan_info['Modelo']}\n"
            fanString += f"Numero de serie: {fan_info['Numero de serie']}\n"
            fanString += f"Descripcion: {fan_info['Descripcion']}\n\n"
            
            
        # Crear el diccionario con la informacion obtenida de cada power supply
        fanDiccionario = {
            'Cantidad de ventiladores': cantidad_fan,
            'Informacion ventiladores': fan_info
        }

        return fanString,fanDiccionario
    except Exception as e:
        return {"Error": f"Error al procesar la información de las power supply: {str(e)}"}
    
def formato_modulos(modulo_info,cantidad_modulo,modelo):
    try:
        moduloString = f"Cantidad de modulos es {cantidad_modulo} en el equipo {modelo}\n\n"
        for i, modulo_info in enumerate(modulo_info, 1):
            moduloString += f"Informacion modulo {i}\n"
            moduloString += f"ID: {modulo_info['Modulo']}\n"
            moduloString += f"Modelo: {modulo_info['Modelo']}\n"
            moduloString += f"Numero de serie: {modulo_info['Numero de serie']}\n"
            moduloString += f"Descripcion: {modulo_info['Descripcion']}\n\n"
            
            
        # Crear el diccionario con la informacion obtenida de cada power supply
        moduloDiccionario = {
            'Cantidad de modulos': cantidad_modulo,
            'Informacion modulos': modulo_info
        }

        return moduloString,moduloDiccionario
    except Exception as e:
        return {"Error": f"Error al procesar la información de las power supply: {str(e)}"}

def ventiladoresCisco(output,modelo):
    try:
        # Utilizamos expresiones regulares para buscar información relevante
        expresionesFan = ('\"(.+)\"\,\s+DESCR:\s+\"(.+[F|f][A-Za-z]{2,2}\s+[T|t][A-Za-z]{3,3}.+)\"\s+PID:\s+([A-Z0-9-]+|\s+)\s+.+SN:\s+(([A-Z0-9-]+|\s+)\s)',
                          '\"([A-Za-z0-9-]{4,4}\s\d+)\"\,\s+DESCR:\s+\"(.+[F|f][A-Za-z]{2,2}.+)\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s',
                          '\"([F|f][A-Za-z]{2,2}\s+\d+)\"\,\s+DESCR:\s+\"([C|c][A-Za-z]{6,6}.+)\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+(.+)',
                          '\"([F|f][A-Za-z]{2,2}\s+\d+)\"\,\s+DESCR:\s+\"(.+[C|c][A-Za-z]{6,6}.+)\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+(.+)'
                          )
        for expresion in expresionesFan:
            matches = re.findall(expresion, output)
            if matches:
                ventiladores = []
                for match in matches:
                    modulo = match [0]
                    descripcion = match[1]
                    pid = match[2]
                    sn = match[4]
                    fan_info = {
                        "Modulo": modulo,
                        "Descripcion": descripcion,
                        "Modelo": pid,
                        "Numero de serie": sn
                    }
                    ventiladores.append(fan_info)
                    dic_sin_repetir=[]
                    for i in ventiladores: 
                        if i not in dic_sin_repetir:
                            dic_sin_repetir.append(i)
                        
                    cantidad_fan = len(dic_sin_repetir)  
                break
            else:
                dic_sin_repetir = []
                cantidad_fan = 0

        return dic_sin_repetir,cantidad_fan
        
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0

def modulosCisco(output,modelo):
    print(f'#################################### MODULOS ####################################')
    try:
        # Utilizamos expresiones regulares para buscar información relevante

        expresionesSupervisor = ('\"([A-Za-z0-9-]{4,4}\s\d+)\"\,\s+DESCR:\s+\"([S|s][A-Za-z]{9,9}.+)\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s',
                                 '\"([A-Za-z0-9-]{6,6}\s\d+)\"\,\s+DESCR:\s+\"(.+[S|s][A-Za-z]{9,9})\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s'
                          )
                
        for expresion in expresionesSupervisor:
            matches = re.findall(expresion, output)
            if matches:
                supervisor = []
                for match in matches:
                    modulo = match [0]
                    descripcion = match[1]
                    pid = match[2]
                    sn = match[4]
                    supervisor_info = {
                        "Modulo": modulo,
                        "Descripcion": descripcion,
                        "Modelo": pid,
                        "Numero de serie": sn
                    }
                    supervisor.append(supervisor_info)
                    dic_sin_repetir_Supervisor=[]
                    for i in supervisor: 
                        if i not in dic_sin_repetir_Supervisor:
                            dic_sin_repetir_Supervisor.append(i) 
                break
            else:
                dic_sin_repetir_Supervisor=[]
                
                
        expresionesEther = ('\"([A-Za-z0-9-]{4,4}\s\d+)\"\,\s+DESCR:\s+\"(.+[E|e][A-Za-z]{7,7}.+)\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s',
                            '°'
                          )
                
        for expresion in expresionesEther:
            matches = re.findall(expresion, output)
            if matches:
                ether = []
                for match in matches:
                    modulo = match [0]
                    descripcion = match[1]
                    pid = match[2]
                    sn = match[4]
                    ether_info = {
                        "Modulo": modulo,
                        "Descripcion": descripcion,
                        "Modelo": pid,
                        "Numero de serie": sn
                    }
                    ether.append(ether_info)
                    dic_sin_repetir_Ether=[]
                    for i in ether: 
                        if i not in dic_sin_repetir_Ether:
                            dic_sin_repetir_Ether.append(i)
                break
            else: 
                dic_sin_repetir_Ether=[]
        
        expresionesGem = ('NAME:\s+\"(.+)\"\,\s+DESCR:\s+\"(.+\s[G|g][A-Za-z]{2,2}.+)\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s',
                          'NAME:\s+\"(.+)\"\,\s+DESCR:\s+\"(.+\s[G|g][A-Za-z]{2,2})\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s'
                          )
                
        for expresion in expresionesGem:
            matches = re.findall(expresion, output)
            if matches:
                gem = []
                for match in matches:
                    modulo = match [0]
                    descripcion = match[1]
                    pid = match[2]
                    sn = match[4]
                    gem_info = {
                        "Modulo": modulo,
                        "Descripcion": descripcion,
                        "Modelo": pid,
                        "Numero de serie": sn
                    }
                    gem.append(gem_info)
                    dic_sin_repetir_gem=[]
                    for i in gem: 
                        if i not in dic_sin_repetir_gem:
                            dic_sin_repetir_gem.append(i)
                break
            else: 
                dic_sin_repetir_gem=[]
                
                
        expresionesFru = ('NAME:\s+\"(.+)\"\,\s+DESCR:\s+\"([F|f][A-Za-z]{2,2}[L|l].+)\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s',
                            '°'
                          )
                
        for expresion in expresionesFru:
            matches = re.findall(expresion, output)
            if matches:
                fru = []
                for match in matches:
                    modulo = match [0]
                    descripcion = match[1]
                    pid = match[2]
                    sn = match[4]
                    fru_info = {
                        "Modulo": modulo,
                        "Descripcion": descripcion,
                        "Modelo": pid,
                        "Numero de serie": sn
                    }
                    fru.append(fru_info)
                    dic_sin_repetir_fru=[]
                    for i in fru: 
                        if i not in dic_sin_repetir_fru:
                            dic_sin_repetir_fru.append(i)
                break
            else: 
                dic_sin_repetir_fru=[]     
                
            expresionesFC = ('NAME:\s+\"(.+)\"\,\s+DESCR:\s+\"(.+[F|f][C|c].+)\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s',
                            '°'
                          )
                
        for expresion in expresionesFC:
            matches = re.findall(expresion, output)
            if matches:
                FC = []
                for match in matches:
                    modulo = match [0]
                    descripcion = match[1]
                    pid = match[2]
                    sn = match[4]
                    fc_info = {
                        "Modulo": modulo,
                        "Descripcion": descripcion,
                        "Modelo": pid,
                        "Numero de serie": sn
                    }
                    FC.append(fc_info)
                    dic_sin_repetir_FC=[]
                    for i in FC: 
                        if i not in dic_sin_repetir_FC:
                            dic_sin_repetir_FC.append(i)
                break
            else: 
                dic_sin_repetir_FC=[]         
        
        dic_sin_repetir = dic_sin_repetir_gem + dic_sin_repetir_Ether + dic_sin_repetir_Supervisor + dic_sin_repetir_fru + dic_sin_repetir_FC
        cantidad_modulos = len(dic_sin_repetir)

        return dic_sin_repetir,cantidad_modulos
        
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0


"""
    Las siguientes funciones sacan la información del switch N2K
"""

def switchn2k(device,version,hostname):
    pattern = '\"(([A-Za-z]{3,3}\s\d+)\s+[C|c][A-Za-z]{6,6})\"\,\s+DESCR:\s+\"(.+)\"\s+PID:\s+([A-Z0-9\-\.]+|\s+)\s.+SN:\s+(.+)'
    matches = re.findall(pattern,device)
    if matches:
        switch = []
        for match in matches:
            marca = 'Cisco'
            modulo = match[0]
            fex = match[1]
            descripcion = match[2]
            modelo = match[3]
            serialNumber = match[4]
            partNumber = modelo
            switch_info = {
                "Marca": marca,
                "Hostname": hostname,
                "Modulo": modulo,
                "Modelo": modelo,
                "Version del firmware": version,
                "Numero de serie": serialNumber,
                "Numero de parte": partNumber,
                "Descripcion": descripcion
            }
            switch.append(switch_info)
            dic_sin_repetir=[]
            for i in switch: 
                if i not in dic_sin_repetir:
                    dic_sin_repetir.append(i)
 
            switchString = f"\nModulo: {switch_info['Modulo']}\nHostname: {switch_info['Hostname']}\nModelo: {switch_info['Modelo']}\nNumero de serie: {switch_info['Numero de serie']}\nNumero de parte: {switch_info['Numero de parte']}\nVersion del firmware: {switch_info['Version del firmware']}\nDescripcion: {switch_info['Descripcion']}\n\n"
            
            patternVentiladores =  '\"(('+fex+')\s+[F|f][A-Za-z]{2,2}\s\d+)\"\,\s+DESCR:\s+\"(.+)\"\s+PID:\s+([A-Z0-9\-\.]+|\s+)\s.+SN:\s+(.+)'
            matches = re.findall(patternVentiladores,device)
            
            if matches:
                ventiladores = []
                for match in matches:
                    modulo = match[0]
                    fex = match[1]
                    descripcion = match[2]
                    modelo = match[3]
                    serialNumber = match[4]
                    partNumber = modelo
                    fan_info = {
                        "Modulo": modulo,
                        "Modelo": modelo,
                        "Numero de serie": serialNumber,
                        "Numero de parte": partNumber,
                        "Descripcion": descripcion
                    }
                    ventiladores.append(fan_info)
                    dic_sin_repetir_fan=[]
                    for i in switch: 
                        if i not in dic_sin_repetir_fan:
                            dic_sin_repetir_fan.append(i)
                fanString = f"Fan: \n\n"
                for i, fan_info in enumerate(dic_sin_repetir_fan, 1):
                    fanString += f"Informacion fan {i}\n"
                    fanString += f"Modulo: {fan_info['Modulo']}\n"
                    fanString += f"Modelo: {fan_info['Modelo']}\n"
                    fanString += f"Descripcion: {fan_info['Descripcion']}\n"
                    fanString += f"PID: {fan_info['Numero de parte']}\n" 
                    fanString += f"Numero de serie: {fan_info['Numero de serie']}\n\n"
                                
            else:
                dic_sin_repetir_fan = []
                fanString = 'No se encontraron ventiladores'
        
            patternPower =  '\"(('+fex+')\s+[P|p][A-Za-z]{4,4}\s.+)\"\,\s+DESCR:\s+\"(.+)\"\s+PID:\s+([A-Z0-9\-\.]+|\s+)\s.+SN:\s+(.+)'
            matches = re.findall(patternPower,device)
            if matches:
                power = []
                for match in matches:
                    modulo = match[0]
                    fex = match[1]
                    descripcion = match[2]
                    modelo = match[3]
                    serialNumber = match[4]
                    partNumber = modelo
                    power_info = {
                        "Modulo": modulo,
                        "Modelo": modelo,
                        "Numero de serie": serialNumber,
                        "Numero de parte": partNumber,
                        "Descripcion": descripcion
                    }
                    power.append(power_info)
                    dic_sin_repetir_power=[]
                    for i in switch: 
                        if i not in dic_sin_repetir_power:
                            dic_sin_repetir_power.append(i)
                powerString = f"Power Supply: \n\n"
                for i, power_info in enumerate(dic_sin_repetir_power, 1):
                    powerString += f"Informacion power supply {i}\n"
                    powerString += f"Modulo: {power_info['Modulo']}\n"
                    powerString += f"Descripcion: {power_info['Descripcion']}\n"
                    powerString += f"PID: {power_info['Numero de parte']}\n" 
                    powerString += f"Numero de serie: {power_info['Numero de serie']}\n\n"
            else:
                dic_sin_repetir_power = []        
                powerString = 'No se encontraron fuentes de poder'               
            
            expresionesSupervisor = '\"(('+fex+')\s+[M|m][A-Za-z]{5,5}\s\d+)\"\,\s+DESCR:\s+\"(.+)\"\s+PID:\s+(([A-Z0-9\-\.]+|\s+)\s).+SN:\s+([A-Z0-9-]+|\s+)\s'
            matches = re.findall(expresionesSupervisor, device)
            if matches:
                supervisor = []
                for match in matches:
                    modulo = match [0]
                    descripcion = match[1]
                    pid = match[2]
                    sn = match[4]
                    supervisor_info = {
                        "Modulo": modulo,
                        "Descripcion": descripcion,
                        "Modelo": pid,
                        "Numero de serie": sn
                    }
                    supervisor.append(supervisor_info)
                    dic_sin_repetir_Supervisor=[]
                    for i in supervisor: 
                        if i not in dic_sin_repetir_Supervisor:
                            dic_sin_repetir_Supervisor.append(i)
                            
                moduloString = f"Modulos\n\n"
                for i, supervisor_info in enumerate(dic_sin_repetir_Supervisor, 1):
                    moduloString += f"Informacion modulo {i}\n"
                    moduloString += f"ID: {supervisor_info['Modulo']}\n"
                    moduloString += f"Modelo: {supervisor_info['Modelo']}\n"
                    moduloString += f"Numero de serie: {supervisor_info['Numero de serie']}\n"
                    moduloString += f"Descripcion: {supervisor_info['Descripcion']}\n\n"
            else:
                dic_sin_repetir_Supervisor = []
                moduloString = 'No hay modulos'
                       
            documentacionEquiposParseo(switch_info,switchString,powerString,fanString,moduloString,device) 
 


"""
Las siguientes funciones XXXXX sacan la informacion de un Switch modular, es decir, el modelo,
numero de serie, numero de parte, version del FW, los datos de los power supply y sus FAN

"""


def formato_cards(cards_info,cantidad_cards,modelo):
    print(f'#################################### Tarjetas ####################################')
    
    try:
        cardsString = f"Cantidad de tarjetas es {cantidad_cards} en el equipo {modelo}\n\n"
        for i, cards_info in enumerate(cards_info, 1):
            cardsString += f"Informacion tarjeta {i}\n"
            cardsString += f"Slot: {cards_info['Slot']}\n"
            cardsString += f"Numero de puertos: {cards_info['Numero de puertos']}\n"
            cardsString += f"Modelo: {cards_info['Modelo']}\n"
            cardsString += f"Numero de serie: {cards_info['Numero de serie']}\n"
            cardsString += f"Descripcion: {cards_info['Descripcion']}\n\n"
            
            
        # Crear el diccionario con la informacion obtenida de cada power supply
        cardsDiccionario = {
            'Cantidad de tarjetas': cantidad_cards,
            'Informacion tarjetas': cards_info
        }

        

        return cardsString,cardsDiccionario
    except Exception as e:
        return {"Error": f"Error al procesar la información de las tarjetas: {str(e)}"}


def formato_sub(sub_info,cantidad_sub,modelo):
    print(f'#################################### Sub Modulos ####################################')
     
    try:
        subString = f"Cantidad de sub-modulos es {cantidad_sub} en el equipo {modelo}\n\n"
        for i, sub_info in enumerate(sub_info, 1):
            subString += f"Informacion modulo {i}\n"
            subString += f"Slot: {sub_info['Modulo']}\n"
            subString += f"Modelo: {sub_info['Modelo']}\n"
            subString += f"Numero de serie: {sub_info['Numero de serie']}\n"
            subString += f"Descripcion: {sub_info['Descripcion']}\n\n"
            
            
        # Crear el diccionario con la informacion obtenida de cada power supply
        subDiccionario = {
            'Cantidad de submodulos': cantidad_sub,
            'Informacion submodulos': sub_info
        }

        

        return subString,subDiccionario
    except Exception as e:
        return {"Error": f"Error al procesar la información de las tarjetas: {str(e)}"}

def subModulosCisco(output,modelo):
    try:
    # Utilizamos expresiones regulares para buscar información relevante
        expresionesSub = ('(\d+)\s+([A-Za-z].+)([V|v|W|w][A-Za-z0-9-]+)\s+([S|s][A-Za-z0-9-]+)\s+\d+\.\d+',
                            '°'
                          )
                
        for expresion in expresionesSub:
            matches = re.findall(expresion, output)
            if matches:
                sub = []
                for match in matches:
                    modulo = match [0]
                    descripcion = match[1]
                    pid = match[2]
                    sn = match[3]
                    sub_info = {
                        "Modulo": modulo,
                        "Descripcion": descripcion,
                        "Modelo": pid,
                        "Numero de serie": sn
                    }
                    sub.append(sub_info)
                    dic_sin_repetir_sub=[]
                    for i in sub: 
                        if i not in dic_sin_repetir_sub:
                            dic_sin_repetir_sub.append(i)
                        
                    cantidad_sub = len(dic_sin_repetir_sub)  
                break
            else:
                dic_sin_repetir_sub = []
                cantidad_sub = 0
                
        return dic_sin_repetir_sub,cantidad_sub
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0

def cardsCisco(output):
    try:
        # Utilizamos expresiones regulares para buscar información relevante
        expresionesCards = ('(\d+)\s+(\d+)\s+(.+)([V|v|W|w][A-Za-z0-9-]+)\s+([S|s][A-Za-z0-9-]+)',
                            '°'
                          )
                
        for expresion in expresionesCards:
            matches = re.findall(expresion, output)
            if matches:
                cards = []
                for match in matches:
                    slot = match [0]
                    ports = match[1]
                    descripcion = match[2]
                    pid = match[3]
                    sn = match[4]
                    cards_info = {
                        "Slot": slot,
                        "Numero de puertos": ports,
                        "Descripcion": descripcion,
                        "Modelo": pid,
                        "Numero de serie": sn
                    }
                    cards.append(cards_info)
                    dic_sin_repetir=[]
                    for i in cards: 
                        if i not in dic_sin_repetir:
                            dic_sin_repetir.append(i)
                        
                    cantidad_cards = len(dic_sin_repetir)  
                break
            else:
                dic_sin_repetir = []
                cantidad_cards = 0
                
        
        return dic_sin_repetir,cantidad_cards
        
    except Exception as e:
            print(f"Ah Ocurrido un error: {e}")
            return 0
                
                

       
def power_supply_cardsCisco(modelo,output):
    try:
        # Utilizamos expresiones regulares para buscar información relevante
        
        expresionesPower = ('\"(.+)\"\,\s+DESCR:\s+\"(.+[P|p][A-Za-z]{4,4}\s+[S|s][A-Za-z]{5,5}\,.+)\"\sPID:\s+([A-Z0-9-]+|\s+)\s.+SN:\s(([A-Z0-9-]+|\s+)\s)',
                            '([P|p][A-Za-z]{4,4}-[S|s][A-Za-z]{5,5}\s+.+\d)\s+\(.+\'(.+)\'\)\s+.+\s+[P|p][A-Za-z]{6,6}\s+[N|n][A-Za-z]{5,5}\s+\=\s+\'([A-Z0-9-]+|\s+)\'\s+.+\s+[S|s][A-Za-z]{5,5}\s+[N|n][A-Za-z]{5,5}\s+\=\s+\'([A-Z0-9-]+|\s+)\'\s+.+\s+[M|m][A-Za-z]{12,12}\s.+[N|n][A-Za-z]{5,5}\s+\=\s+\'([0-9-]+|\s+)\''
                            )
        
        for expresion in expresionesPower:
            matches = re.findall(expresion, output)
            if matches:
                # Creamos una lista de diccionarios para almacenar la información de cada suministro de energía
                power_supply_info = []
                for match in matches:
                    modulo = match[0]
                    descripcion = match[1]
                    pid = match[2]
                    sn = match[3]
                    part=match[4]
                    power_info = {
                        "Modulo": modulo,
                        "Descripcion":descripcion,
                        "Product Number": part,
                        "Numero de parte": pid,
                        "Numero de serie": sn
                    }
                    
                    power_supply_info.append(power_info)
                break
            else:
                power_supply_info = []
                cantidad_power_supply = 0
        

        #las siguientes lineas de codigo son para quitar los elementos repetidos en un diccionario        
        dic_sin_repetir=[]
        for i in power_supply_info:
            if i not in dic_sin_repetir:
                dic_sin_repetir.append(i) 
        
        # Contamos la cantidad de power supply
        cantidad_power_supply = len(dic_sin_repetir)

        return dic_sin_repetir,cantidad_power_supply
    except Exception as e:
        return {"Error": f"Error al procesar la informacion de las power supply {str(e)}"}

def detectarMarca(cadena):
    if re.search(r'brocade', cadena, re.IGNORECASE):
        return "brocade"
    elif re.search(r'cisco', cadena, re.IGNORECASE):
        return "cisco"
    elif re.search(r'foundry networks', cadena, re.IGNORECASE):
        return "brocade mod"
    else:
        return "Marca no reconocida"


if __name__ == '__main__':
    main('output.txt')