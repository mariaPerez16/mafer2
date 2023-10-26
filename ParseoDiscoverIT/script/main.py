import Funciones


def main():
    device_config, commands_config, device = Funciones.conexion('config.yaml')
    try:
      #print(f'########################{device_config}###################################')
      # Ejecutar el comando 'show version'
      version_output = device.cli([commands_config['version']])
      #print(f'Estoy en el try: {version_output}')
      cadena = version_output['show version']

      marca = Funciones.detectarMarca(cadena)
        
      # Ejecutar los comandos correspondientes a la marca detectada
      if marca in commands_config:
        Funciones.execute_commands(device, commands_config[marca])

        device.close()
      Funciones.main('output.txt')


    except Exception as e:
        print(f"Error ocurrido en main: {str(e)}")
    

if __name__ == "__main__":
    main()
