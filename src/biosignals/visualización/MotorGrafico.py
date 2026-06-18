 #Clase MotorGráfico
import matplotlib.pyplot as plt
import numpy as np
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.epocas.Epocas import Epocas

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
    
    #Métodos de visualización
    
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
    def graficar_por_renglones(self, mostrar: bool = True):
        """
        Grafica los canales seleccionados en renglones separados (subplots)
        para evitar que se superpongan las señales.
        """
        if self.senal_actual is None:
            raise ValueError("No hay ninguna señal cargada para graficar.")
            
        # 1. Filtrar los canales que el usuario quiere ver
        canales_a_ver = self.canales_visibles if self.canales_visibles else self.senal_actual.info.nombre_canales
        n_canales = len(canales_a_ver)
        
        if n_canales == 0:
            raise ValueError("No se seleccionaron canales válidos para graficar.")

        # 2. Configurar ventanas de tiempo usando tus propiedades
        fs = self.senal_actual.info.frecuencia_muestreo
        if self.rango_tiempo:
            tmin, tmax = self.rango_tiempo
            idx_inicio = max(0, int(tmin * fs))
            idx_fin = min(self.senal_actual.n_samples(), int(tmax * fs))
        else:
            idx_inicio, idx_fin = 0, self.senal_actual.n_samples()

        vector_tiempo = np.arange(idx_inicio, idx_fin) / fs

        # 3. Crear la figura con múltiples renglones (sharex=True para sincronizar el zoom temporal)
        fig, axes = plt.subplots(nrows=n_canales, ncols=1, figsize=(12, 2 * n_canales), sharex=True)
        
        # Corrección si es un solo canal (para que siga siendo indexable)
        if n_canales == 1:
            axes = [axes]

        # 4. Iterar y graficar canal por canal
        for i, nombre_ch in enumerate(canales_a_ver):
            # Usamos el método get_data de tu RawSignal
            datos_canal = self.senal_actual.get_data(picks=[nombre_ch])[0, idx_inicio:idx_fin]
            
            # Restamos la media para centrar y que luzca clínico
            datos_canal_centrados = datos_canal - np.mean(datos_canal)
            
            # Dibujar en su renglón correspondiente
            axes[i].plot(vector_tiempo, datos_canal_centrados, linewidth=0.8)
            
            # Nombre del canal a la izquierda en horizontal
            axes[i].set_ylabel(nombre_ch, rotation=0, labelpad=20, fontsize=10, fontweight='bold')
            axes[i].grid(True, linestyle='--', alpha=0.5)

        # Configurar el eje de tiempo final en el último renglón
        axes[-1].set_xlabel("Tiempo (segundos)", fontsize=12)
        fig.suptitle("Visualización por Renglones Independientes", fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if mostrar:
            plt.show()

    # Métodos de visualización: Épocas

    def graficar_epocas(self, mostrar: bool = True):
        """
        Grafica todas las épocas disponibles una al lado de la otra (Subplots).
        Cumple con el requerimiento de la Figura lado a lado del PDF.
        """
        if self.epocas is None or len(self.epocas) == 0: 
            raise ValueError("No hay épocas disponibles para graficar.")
        
        data = self.epocas.get_data() 
        num_epocas = len(data)

        # Creamos una figura con subplots lado a lado (1 fila, N columnas)
        fig, axes = plt.subplots(1, num_epocas, figsize=(4 * num_epocas, 4), sharey=True)
        
        # Si solo hay una época, axes no es un array, lo convertimos a lista para iterar
        if num_epocas == 1:
            axes = [axes]

        for i, (epoca, ax) in enumerate(zip(data, axes)):
            ax.plot(epoca.T)
            ax.set_title(f"Época {i}")
            ax.set_xlabel("Muestras")
            if i == 0:
                ax.set_ylabel("Amplitud") # Solo ponemos el label Y en el primer gráfico
        
        plt.tight_layout() # Ajusta los márgenes para que no se superpongan
        
        if mostrar:
            plt.show()
        
    def graficar_epoca(self, indice: int, mostrar: bool = True): 
        """
        Grafica una época específica por su índice.
        """
        if self.epocas is None or len(self.epocas) == 0: 
            raise ValueError("No hay épocas cargadas.")
        
        data = self.epocas.get_data() # Unificado a get_data()

        if indice < 0 or indice >= len(data):
            raise IndexError(f"El índice {indice} está fuera de rango. Hay {len(data)} épocas.")

        epoca = data[indice] 
        
        plt.figure(figsize=(8, 4))
        plt.plot(epoca.T)
        plt.title(f"Época {indice}")
        plt.xlabel("Muestras")
        plt.ylabel("Amplitud")
        
        if mostrar:
            plt.show()

    def graficar_tiempo_frecuencia_epocas(self, indices_epocas: list[int] = None, mostrar: bool = True):
        """
        Grafica la representación en tiempo-frecuencia para una o más épocas.
        Cumple con el requisito del PDF: cada época en una NUEVA ventana.
        """
        if self.epocas is None or len(self.epocas) == 0: 
            raise ValueError("No hay épocas cargadas.")

        # Solicitamos la matriz de tiempo-frecuencia ya calculada a la clase Epocas
        espectro = self.epocas.tiempo_frecuencia()
        
        # Si no se pasan índices, graficamos todas
        indices = indices_epocas if indices_epocas is not None else range(len(self.epocas))

        for i in indices:
            if i >= len(self.epocas):
                continue
            
            # plt.figure() asegura que cada época se abra en una ventana nueva independiente
            plt.figure(figsize=(8, 4)) 
            
            # Espectrograma simple usando imshow
            plt.imshow(espectro[i, 0].reshape(1, -1), aspect='auto', cmap='viridis')
            
            plt.title(f"Tiempo-Frecuencia - Época {i}")
            plt.xlabel("Frecuencia (Bins)")
            plt.ylabel("Amplitud (FFT)")
            plt.colorbar(label='Magnitud')
            
        if mostrar:
            plt.show()
    
    #Métodos de Eventos y Anotaciones

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
        lista_eventos = eventos.get_events()

        #Recorremos eventos
        for evento in lista_eventos:
            muestra = evento[0] #posición de emuestr donde ocurre el evento
            id_evento = evento[1] #tipo de evento, identificador de el tipo de evento

            #Dibujamos la línea vertical
            plt.axvline(x = muestra, linestyle = "--") 
            #Agrregamos una etiqueta
            plt.text(muestra, plt.ylim()[1], str(id_evento), rotation = 90) 

    #Métodos de configuración

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

    #Métodos de Actualización y Limpieza

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

    #Métodos de exportación

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

    
        