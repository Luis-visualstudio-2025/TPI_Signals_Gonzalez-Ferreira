#Clase MotorGráfico
import matplotlib.pyplot as plt
import numpy as np
#import plotly.graph_objects as go, esta libreria tal vez la uso pero aún no se

"""
El motor gráfico deber ser independiente del tipo de señal biomédica.
Debe funcionar con cualquier señal organizada como: canales x muesrras.
Por ejemplo:
ECG -> una o pocas derivaciones
EEG -> muchos canales
EMG -> cantidad variable de canales
"""


class MotorGrafico():

    """
    Motor de visualización genérico para señales biomédicas.
    La clase permite visualizar señales multicanal y épocas, independientemente del tipo de señal biompedica (ECG, EEG, EMG, etc.).
    El motor asume que las señales están organizadas con forma: canales x muestras.
    """
    def __init__(self,senal_actual : RawSignal,epocas : Epocas,modo_visualizacion : str,canales_visibles : list[str],mostrar_anotaciones : bool,rango_tiempo : tuple[float,float]):

        """
        Inicializa el motor gráfico.

        Parámetros
        ----------

        senal_actual : RawSignal  #Señal biomédica actual a visualizar
        epocas : Epocas  #Conjunto de épocas asociadas a la señal
        modo_visualización : str  #Modo de visualización actual, puede ser "señal" o "épocas".
        canales_visibles : list[str]  #Lista de canales a visualizar.
        mostrar_anotaciones : bool  #Indica si se deben mostrar eventos/notaciones
        rango_tiempo : tuple[float, float]  #Intervalo temporal a visualizar en segundos.
        """

        self.senal_actual = senal_actual
        self.epocas = epocas
        self.modo_visualizacion = modo_visualizacion
        self.canales_visibles = canales_visibles
        self.mostrar_anotaciones = mostrar_anotaciones
        self.rango_tiempo = rango_tiempo
    

    #::::::::::::::::::::::::::
    #Métodos de visualización
    #::::::::::::::::::::::::::

    def graficar_senal(self, mostrar=True):
        """
        Grafica la señal biomédica actual.
        La señal debe tener la forma: canales x muestras.
        """
        #Verificamos que exista una señal cargada
        if self.senal_actual is None: 
            raise ValueError("No se encuentra una señal cargada")
        #Obtenemos los canales seleccionados
        if self.canales_visibles is not None:
            data = self.senal_actual.get_data(self.canales_visibles)
        #Si no se especifican canales se grafican todos
        else:
            data = self.senal_actual.get_data()
        #SAplicamos recorte temporal si existe
        if self.rango_tiempo is not None:
            inicio,fin = self.rango_tiempo
            #Frecuencia de muestreo
            fs = self.senal_actual.info.frecuencia_muestreo
            #Conversión de segundos a muestras
            inicio_muestra = int(inicio*fs)
            fin_muestra = int(fin*fs)
            #Recorte temporal
            data = data[:,inicio_muestra:fin_muestra]
        
        #Trasponemos la matriz para que matplotlib interprete cada canal como una línea independiente
        plt.plot(data.T)

        plt.title("Señal")
        plt.xlabel("Muestras")
        plt.ylabel("Amplitud")

        #Mostramos eventos si corresponde
        if self.mostrar_anotaciones:
            self.resaltar_eventos()
        
        #Mostramos 
        if mostrar:
            plt.show()

    def graficar_epocas(self, mostrar = True):
        """
        Grafica todas las épocas disponibles.
        """

        #Verificamos que existan épocas
        if self.epocas is None: 
            raise ValueError("No hay Épocas disponibles")
        
        #Obtenemos las épocas
        data = self.epocas.get_data() 
        #Recorremos y graficamos cada época
        for i, epoca in enumerate(data):
            plt.plot(epoca.T)
            plt.title(f"Época{i}")
            plt.xlabel("Muestras")
            plt.ylabel("Amplitud")

            if mostrar:
                plt.show()
        
    def graficar_epoca(self, indice: int): 
        """
        Grafica una época específica.

        Parámetros
        ----------
        indice : int  #Índice de la época a visualizar
        """
        #Verificamos que existan épocas
        if self.epocas is None: 
            raise ValueError("No hay época cargada")
        
        #Obtenemos todas las épocas
        data = self.epocas.get_data() 

        #Seleccionamos la época deseada
        epoca = data[indice] 
        #Graficamos
        plt.plot(epoca.T)
        
        plt.title(f"Época{indice}")
        plt.xlabel("Muestras")
        plt.ylabel("Amplitud")
        plt.show()
    
    #::::::::::::::::::::::::::::::::::
    #Métodos de Eventos y Anotaciones
    #::::::::::::::::::::::::::::::::::

    def resaltar_eventos(self):
        """
        Muestra los eventos asociados a la señal mediante líneas verticales.
        """
        #Verificamos que exista señal
        if self.senal_actual is None:
            raise ValueError("No hay señal cargada")
        
        #Obtenemos objeto eventos
        eventos = self.senal_actual.eventos

        #Verificamos que existan eventos
        if eventos is None:
            raise ValueError("No hay eventos asociados")
        
        #Lista de eventos : [(muestra, id_evento), ...]
        lista_eventos = eventos.get_eventos()

        #Recorremos eventos
        for evento in lista_eventos:
            muestra = evento[0] #posición de emuestr donde ocurre el evento
            id_evento = evento[1] #tipo de evento, identificador de el tipo de evento

            #Dibujamos la línea vertical
            plt.axvline(x = muestra, linestyle = "--") 
            #Agrregamos una etiqueta
            plt.text(muestra, plt.ylim()[1], str(id_evento), rotation = 90) 

    #::::::::::::::::::::::::::
    #Métodos de configuración
    #::::::::::::::::::::::::::

    def seleccionar_intervalo(self, inicio : float, fin : float):
        """
        Define el intervalo temporal a visualizar.

        Parámetros
        ----------
        inicio : float  #Timepo inicial en segundos
        fin : float  #Tiempo final en segundos
        """

        #Verificamos que el intervalos ea válido
        #Contrato:
        #El inicio debe ser menor al fin
        if inicio >= fin:
            raise ValueError("El inicio debe ser menor que el fin")
        #Guardamos el intervalo
        self.rango_tiempo = (inicio,fin)
        #NO OLVIDAR AGREGAR EL ATRIBUTO rango_tiempo EN EL DIAGRAMA UML DE LA CLASE MOTORGRAFICO

    #:::::::::::::::::::::::::::::::::::::
    #Métodos de Actualización y Limpieza
    #:::::::::::::::::::::::::::::::::::::

    def actualizar(self):
        """
        Actualiza la visualización actual.
        """
        #Limpiamos la figura anterior
        plt.clf()

        #El modo de visualización determina qué representación gráfica utilizar
        if self.modo_visualizacion == "señal":
            self.graficar_senal()
        
        elif self.modo_visualizacion == "epocas":
            self.graficar_epocas()

        else:
            raise ValueError("Modo de visualización incorrecto")
    
    def limpiar(self):
        """
        Limpia la figura actual y reinicia el rango temporal.
        """
        #Limpiamos la figura
        plt.clf()
        #Cerramos la ventana
        plt.close() 
        #Reiniciamos el intervalo 
        self.rango_tiempo = None 

    #::::::::::::::::::::::::
    #Métodos de exportación
    #::::::::::::::::::::::::

    def guardar_imagen(self,path : str):
        """
        Guarda la visualización actual en disco.

        Parámetros
        ----------
        path : str  #Ruta del archivo de salida
        """
        #Verificamos que exista algo para graficar
        if self.senal_actual is None and self.epocas is None:
            raise ValueError("No hay nada que graficar")
        
        #Reutilizamos los métodos de graficación, para evitar duplicación lógica
        if self.modo_visualizacion == "señal":
            self.graficar_senal(mostrar=False)
        
        elif self.modo_visualizacion == "epocas":
            self.graficar_epocas(mostrar=False)

        else:
            raise ValueError("Modo de visualización no válido")
        
        #Guardamos la figura
        plt.savefig(path)

        #Cerramos la figura, es para liberar memoria por las dudas
        plt.close()
   
        #Probar si grafica señales de 1xN, o 3xN etc, si es lo suficiente general


        