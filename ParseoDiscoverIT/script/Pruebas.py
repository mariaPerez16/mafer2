import re
import os

def crear_carpeta(nombre):
# Se define el nombre de la carpeta o directorio a crear
    ruta_actual = os.getcwd()
    #print("La ruta del directorio actual es:", ruta_actual)
    directorio = f'{ruta_actual}/' + nombre #checar ruta
    print(f'no esta creando directorios: {directorio}')
    try:
        os.mkdir(directorio)
    except OSError:
        print("La creación del directorio %s falló" % directorio)
    else:
        print("Se ha creado el directorio: %s " % directorio)

def detectarMarca(cadena):
    if re.search(r'brocade', cadena, re.IGNORECASE):
        return "brocade"
    elif re.search(r'cisco', cadena, re.IGNORECASE):
        return "cisco"
    elif re.search(r'foundry networks', cadena, re.IGNORECASE):
        return "brocade mod"
    if re.search(r'brocade', cadena, re.IGNORECASE):
        return "brocade"
    elif re.search(r'cisco', cadena, re.IGNORECASE):
        return "cisco"
    elif re.search(r'foundry networks', cadena, re.IGNORECASE):
        return "brocade mod"
    else:
        return "Marca no reconocida"

def abrir_archivo(archivo):
    with open(archivo, 'r') as archivo:
        contenido = archivo.read()
    return contenido


def parse_switch_units_brocade(output):
    units = []
    unit_pattern = re.compile(r"Switch\s+(\d+)\s+(.+)\n.+Serial\s*#: (\S+)", re.DOTALL)
    unit_matches = unit_pattern.findall(output)
    Management_Module = 'Management Module'
    count_mm = 1  # Start counting from 1
    count = 0
    for unit in unit_matches:
        if Management_Module in unit[1]:
            nueva = unit[2]  # Extract the serial number
            nueva = tuple([nueva])
            units.append(unit + nueva)
            count += 1
        else:
            units.append(unit)
        count_mm += 1
    if units == []:
        pass
    else:
        units = sorted(units, key=lambda tupla: int(tupla[0])) # buscar el numero de la unidad

    return units


def obtener_modelo_chassis_brocade_modular(resultado):
    lineas = resultado.split("\n")  # Dividir el resultado en líneas
    for linea in lineas:
        if "Chassis Type:" in linea:
            modelo_chassis = linea.split(":")[-1].strip()  # Extraer el modelo del chassis
            return modelo_chassis
    return None  # Si no se encuentra el modelo del chassis


def obtener_estado_power_supply(resultado):
    lineas = resultado.split("\n")
    power_supply = []
    for linea in lineas:
        if linea.startswith("Power supply"):
            estado = linea.split()[-1]
            power_supply.append(estado)
    total = len(power_supply)
    funcionando = power_supply.count("ok")
    no_funcionando = total - funcionando
    return total, funcionando, no_funcionando

def encontrar_version(texto):
    # Define el patrón de expresión regular para buscar la versión del software (SW).
    patron = r'SW: Version ([^\s]+)'

    # Busca el patrón en el texto de entrada.
    coincidencias = re.search(patron, texto)

    # Si se encontró una coincidencia, devuelve la versión del software.
    if coincidencias:
        version_sw = coincidencias.group(1)
        return version_sw
    else:
        return 'Versión no encontrada'
    
def encontrar_hostname(salida):
    # Utiliza una expresión regular para encontrar el nombre de host
    regex_hostname = r"hostname (\w+)"
    match = re.search(regex_hostname, salida)
    
    if match:
        # Si se encuentra un nombre de host, devuélvelo
        return match.group(1)
    else:
        # Si no se encuentra un nombre de host, devuelve None o un valor predeterminado según tu preferencia
        return None
    
def encontrar_fuentes_info(salida):
    # Buscar la información de las fuentes de alimentación
    regex_fuente = r"Power supply (\d+) \((\d+) - (.+?)\)"
    matches_fuente = re.findall(regex_fuente, salida)
    # contar fuentes
    regex_fuente_total = r"Power supply"
    matches_fuente_total = re.findall(regex_fuente_total, salida)
    # Imprimir información de las fuentes
    if matches_fuente:
        print(f"total de fuentes: {len(matches_fuente_total)}")
        
        fuentes_presentes = [fuente for fuente in matches_fuente if fuente[0] != "not present"]
        #fuentes_no_presentes = [fuente for fuente in matches_fuente if fuente[0] == "not present"]

        print(f"fuentes presentes: {len(fuentes_presentes)}")
        print(f"fuentes no presentes: {len(matches_fuente_total) - len(fuentes_presentes)}")
        
        for fuente in matches_fuente:
            numero_fuente = fuente[0]
            no_parte = fuente[1]
            descripcion = fuente[2]
            print(f"No. parte fuente {numero_fuente}: {no_parte}")
            print(f"Descripción: Power supply {numero_fuente} ({no_parte} - {descripcion})\n")

        return matches_fuente
    else:
        print("No se encontraron fuentes de alimentación.")
        return 0

def obtener_informacion_fan_brocade(texto):
    # Dividir el texto en líneas
    lines = texto.split('\n')

    # Buscar información de los FAN
    fan_info = {}
    fan_speed_info = {}
    for line in lines:
        if "Fan" in line:
            parts = line.split()
            fan_number = parts[1]
            status = parts[-1]
            fan_info[fan_number] = status
            if "speed (auto)" in line:
                fan_speed_info[fan_number] = line

    # Contar la cantidad de FAN
    num_fans = len(fan_info)

    return num_fans, fan_info, fan_speed_info

archivo = abrir_archivo('output.txt')
print(archivo)
print()
print(f'DONDE ESTA {detectarMarca(archivo)}')

units = parse_switch_units_brocade(archivo)
print(units)

total, funcionando, no_funcionando = obtener_estado_power_supply(archivo)
print("Total Power Supply:", total)
print("Funcionando:", funcionando)
print("No funcionando:", no_funcionando)

version = encontrar_version(archivo)
print(f'Version del Firmware: {version}')

host = encontrar_hostname(archivo)
print(f'Este es el HostName: {host}')

fuentes = encontrar_fuentes_info(archivo)
print(fuentes)

num_fans, fan_info, fan_speed_info = obtener_informacion_fan_brocade(archivo)
# Imprimir el número de ventiladores
print(f"Número de ventiladores: {num_fans}")

# Imprimir la información de los ventiladores por separado
for fan, status in fan_info.items():
    print(f"Fan {fan}: {status}")

# Imprimir la información de velocidad de los ventiladores
for fan, speed_info in fan_speed_info.items():
    print(f"Fan {fan} Speed Info: {speed_info}")




