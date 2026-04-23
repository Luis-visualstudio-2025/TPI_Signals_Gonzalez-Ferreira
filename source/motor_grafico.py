#Código para el motor gráfico
#Para que esta clase funcione necesitamos las clases RawSignal y Epocas
#Importo librerias de plt 
import matplotlib.pyplot as plt
#import plotly.graph_objects as go, esta libreria tal vez la uso pero aún no se

#Voy a crear mocks de RawSignal, Epocas, Info y Eventos para probar si la clase MotorGrafico funciona
#class Info:
  #  def __init__(self):
 #       self.frecuencia_muestreo = 100 #Hz

#class Eventos:
    #def __init__(self):
        #lista de (muestra,id_evento)
   #     self._eventos = [(50,1),(150,2),(300,3)]

  #  def get_eventos(self):
 #       return self._eventos

#class RawSignal:
   # def __init__(self):
   #     import numpy as np

  #      self.info = Info()
 #       self.eventos = Eventos()

        #señal fake de 2 canales
#        self._data = [np.sin(np.linspace(0,100,500)),np.cos(np.linspace(0,100,500))]
    
    #def get_data(self, picks = None):
        #return self._data

#class Epocas:
#   def __init__(self):
#       import numpy as np

        # 3 épocas, cada una con 2 canales
#       self._data = [[np.random.randn(100), np.random.randn(100)],[np.random.randn(100), np.random.randn(100)],[np.random.randn(100), np.random.randn(100)]]

#   def get_data(self):
#       return self._data

class MotorGrafico(): #creo la clase MotorGrafico
    def __init__(self,senal_actual : RawSignal,epocas : Epocas,modo_visualizacion : str,canales_visibles : list[str],mostrar_anotaciones : bool,rango_tiempo : tuple[float,float]): #defino los atributos de la clase
        self.senal_actual = senal_actual
        self.epocas = epocas
        self.modo_visualizacion = modo_visualizacion
        self.canales_visibles = canales_visibles
        self.mostrar_anotaciones = mostrar_anotaciones
        self.rango_tiempo = rango_tiempo
    

    #Métodos de la clase MotorGráfico, esto podemos modificarlo después.
    #Grafico la señal
    def graficar_senal(self, mostrar=True):
        if self.senal_actual is None: #verifico que tengamos una señal cargada
            raise ValueError("No se encuentra una señal cargada")
        
        data = self.senal_actual.get_data(picks=self.canales_visibles) #obtengo los datos de los canales seleccionados
        #Si hay un intervalo seleccionado, lo aplico
        if self.rango_tiempo is not None:
            inicio,fin = self.rango_tiempo

            fs = self.senal_actual.info.frecuencia_muestreo
            inicio_muestra = int(inicio*fs)
            fin_muestra = int(fin*fs)
            #recorto cada canal
            data = [canal[inicio_muestra:fin_muestra]for canal in data]

        for canal in data:
            plt.plot(canal)

        #get_data() método de RawSignal, lo definimos en la clase RawSignal.Me sirve para obtener los datos de la señal 
        plt.title("Señal")
        plt.xlabel("Muestras")
        plt.ylabel("Amplitud")

        if self.mostrar_anotaciones: #resalto eventos con el método resaltar_eventos que está más abajo?, está bien?, no estoy seguro.
            self.resaltar_eventos()

        if mostrar:
            plt.show()

    #Grafico épocas y época
    def graficar_epocas(self, mostrar = True):
        if self.epocas is None: #verifico que haya épocas cargadas
            raise ValueError("No hay Épocas disponibles")
        
        data = self.epocas.get_data() #obtengo los datos de las épocas
        #recorremos las épocas con el for 
        for i, epoca in enumerate(data):
            for canal in epoca:
                plt.plot(canal)
            plt.title(f"Época{i}")
            if mostrar:
                plt.show()
        
    def graficar_epoca(self, indice: int): #este método es para graficar CADA época
        if self.epocas is None: #de nuevo, verifico que haya épocas
            raise ValueError("No hay época cargada")
        data = self.epocas.get_data() #obtengo las épocas

        epoca = data[indice] #según el índice elijo la época que quiero
        for canal in epoca:
            plt.plot(canal)
        
        plt.title(f"Época{indice}")
        plt.xlabel("Muestras")
        plt.ylabel("Amplitud")
        plt.show()
    
    #Resaltar eventos
    def resaltar_eventos(self):
        #if self.senal_actual is None:
         #   print("No hay señal cargada")
          #  return
        eventos = self.senal_actual.eventos #obtengo objeto evento de la señal

        if eventos is None:
            print("No hay eventos")
            return
        
        lista_eventos = eventos.get_eventos()#obtenemos la lista de eventos usando el método get_eventos de la clase Eventos, la lista sería algo como: [(muestra,id_evento)...]

        #Recorremos cada evento
        for evento in lista_eventos:
            muestra = evento[0] #posición de emuestr donde ocurre el evento
            id_evento = evento[1] #tipo de evento, identificador de el tipo de evento

            plt.axvline(x = muestra, linestyle = "--") #dibujp una línea vertical en la posición del evento
            plt.text(muestra, 0, str(id_evento), rotation = 90) #etiquete con el id del evento
    
    def seleccionar_intervalo(self, inicio : float, fin : float):
        #Me combiene verificar que el intervalo sea válido
        if inicio >= fin:
            raise ValueError("Intervalo incorrecto") #no es correcto pero no me sale la palabra, es que el inicio no puede ser mayor que el fin por eso es incorrecto.
        self.rango_tiempo = (inicio,fin) #guardo el intervalo (¿el método seleccionar_intervalo y el de resaltar_eventos iría dentro de graficar_senal?)
        #NO OLVIDAR AGREGAR EL ATRIBUTO rango_tiempo EN EL DIAGRAMA UML DE LA CLASE MOTORGRAFICO

    #método actulizar 
    def actualizar(self): #limpio antes de graficar de nuevo
        plt.clf()

        #según el modo de visualización elijo que quiero graficar 
        if self.modo_visualizacion == "señal":
            self.graficar_senal()
        
        elif self.modo_visualizacion == "epocas":
            self.graficar_epocas()

        else:
            raise ValueError("Modo de visualización incorrecto")
    
    #método limpiar
    def limpiar(self):
        plt.clf()

        plt.close() #cierro la ventana del gráfico, esto es opcional, lo podemos quitar.

        self.rango_tiempo = None #reseteo el intervalo seleccionado.

    #guardo la imagen
    def guardar_imagen(self,path : str): #Verifico si hay algo para guardar 
        if self.senal_actual is None and self.epocas is None:
            raise ValueError("No hay nada que graficar")
        #genero el gráfico a partir del modo de visualizacion actual
        if self.modo_visualizacion == "señal":
            self.graficar_senal(mostrar=False)
        
        elif self.modo_visualizacion == "epocas":
            self.graficar_epocas(mostrar=False)

        else:
            raise ValueError("Modo de visualización no válido")
        
        #guardo la figura acutal en el archivo indicado
        plt.savefig(path)

        #cierro la figura, es para liberar memoria por las dudas
        plt.close()

# Crear objetos fake
#raw = RawSignal()
#epocas = Epocas()

# Crear motor
#motor = MotorGrafico(senal_actual=raw,epocas=epocas,modo_visualizacion="señal",canales_visibles=["C1", "C2"],mostrar_anotaciones=True,rango_tiempo=(0, 3))

# Probar métodos
#motor.graficar_senal()
#motor.graficar_epocas()
#motor.guardar_imagen("test.png")
            
        

        