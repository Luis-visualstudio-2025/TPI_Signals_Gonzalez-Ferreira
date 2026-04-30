import pandas as pd
from collections import Counter

class Anotaciones:
    def __init__(self, onset, duration, description, t0=None, ch_names=None):
        self.onset = onset
        self.duration = duration
        self.description = description
        self.t0 = t0
        self.ch_names = ch_names
    def __iter__(self):
        return iter(zip(self.onset, self.duration, self.description))
    def __len__(self):
        return len(self.onset)
    def __str__(self):
        conteo_descripciones = Counter(self.description)
        return f"Anotaciones: {len(self.onset)} anotaciones, Tipos: {dict(conteo_descripciones)}"
    def add(self, onset, duration, description):
        self.onset.append(onset)
        self.duration.append(duration)
        self.description.append(description)
    def remove(self, index):
        del self.onset[index]
        del self.duration[index]
        del self.description[index]
    def get_annotations(self):
        return pd.DataFrame({'onset': self.onset,'duration': self.duration,'description': self.description,'t0': self.t0,'ch_names': self.ch_names })
    def find(self, description):
        df = self.get_annotations()
        return df[df['description'] == description]
    def save(self, filename):
        df = self.get_annotations()
        df.to_csv(filename, index=False)
    def load(self, filename):
        df = pd.read_csv(filename)
        self.onset = df['onset'].tolist()
        self.duration = df['duration'].tolist()
        self.description = df['description'].tolist()
        self.t0 = df['t0'].iloc[0] if 't0' in df.columns else None
        self.ch_names = df['ch_names'].iloc[0] if 'ch_names' in df.columns else None


class Eventos:
    def __init__(self, eventos):
        self.eventos = eventos
    def __iter__(self):
        return iter(self.eventos)
    def __len__(self):
        return len(self.eventos)
    def __str__(self):
        conteo_eventos = Counter([evento[1] for evento in self.eventos])
        return f"Eventos: {len(self.eventos)} eventos, Tipos: {dict(conteo_eventos)}"
    def add(self, muestra, id_evento):
        self.eventos.append((muestra, id_evento))
    def remove(self, index):
        del self.eventos[index]
    def get_events(self):
        return pd.DataFrame(self.eventos, columns=['muestra', 'id_evento'])
    def find(self, id_evento):
        df = self.get_events()
        return df[df['id_evento'] == id_evento]
    def save(self, filename):
        df = self.get_events()
        df.to_csv(filename, index=False)
    def load(self, filename):
        df = pd.read_csv(filename)
        self.eventos = list(zip(df['muestra'], df['id_evento']))


# Ejemplo de uso de las clases Anotaciones y Eventos
if __name__ == "__main__":
    anotaciones = Anotaciones(onset=[0, 10, 20], duration=[5, 5, 5], description=['artefacto', 'movimiento', 'cansancio'])
    print(anotaciones)
    eventos = Eventos(eventos=[(100, 1), (200, 2), (300, 1)])
    print(eventos)