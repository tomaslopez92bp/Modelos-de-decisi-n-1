import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from scipy.stats import triang

class ProjectGraph:
    def __init__(self):
        self.n = 14
        self.m = 6
        self.paths = self._load_paths()
        self.dist_params = self._load_tasks_dist_params()

    def get_paths(self):
        return self.paths

    def get_n_tasks(self):
        return self.n

    def get_tasks_dist_params(self):
        return self.dist_params

    def _load_tasks_dist_params(self):
        # Define los parametros de la distribucion triang para cada tarea.
        # Notar que es estatico, pero podria ser dinamico (tomarse de alguna
        # otra fuente). Usa un diccionario.
        d = {}
        d[0] = (1.0, 2.0, 3.0)
        d[1] = (2.0, 3.5, 8.0)
        d[2] = (6.0, 9.0, 18.0)
        d[3] = (4.0, 5.5, 10.0)
        d[4] = (1.0, 4.5, 5.0)
        d[5] = (4.0, 4.0, 10.0)
        d[6] = (5.0, 6.5, 11.0)
        d[7] = (5.0, 8.0, 17.0)
        d[8] = (3.0, 7.5, 9.0)
        d[9] = (3.0, 9.0, 9.0)
        d[10] = (4.0, 4.0, 4.0)
        d[11] = (1.0, 5.5, 7.0)
        d[12] = (1.0, 2.0, 3.0)
        d[13] = (5.0, 5.5, 9.0)
        return d

    def _load_paths(self):
        # Define los caminos. 
        # Notar que es estatico. Podria ser conveniente tener otra
        # representacion e, incluso, otra estructura para el grafo general.
        return [[0,1,2,3,6,7,12],[0,1,2,4,7,12],[0,1,2,4,5,9,10,13],[0,1,2,4,5,9,11,13],[0,1,2,8,9,10,13],[0,1,2,8,9,11,13]]

def simulate_triangular(op,ml,ps):
    # TP1 TODO: Completar codigo
    # Esta funcion toma los 3 parametros de la distribucion triangular
    # y devuelve un numero psuedo-aleaotrio con esta distribucion.
    # Tenemos que adaptar estos parametros a lo que recibe la funcion
    # triang.ppf para aplicar el metodo de la transformada inversa. .

    # Primero un chequeo: si op == ps, entonces no hay mucho para simular.
    # Por que?
    # Porque se estaria generando un número entre op y ps, pero, al estos tener
    # el mismo valor solo existe un solo valor posible.
    if op == ps:
        return ml

    # Esta es la traduccion de parametros a realizar scipy.stats. Revisar la documentaicon
    # y entender como se representa la distribucion.
    #loc = op
    #scale = (ps - op)
    #c = (ml - loc)/scale

    # Si usan numpy.random, no son necesarias traducciones.
    else:
        x = random.random()
        loc = op
        scale = (ps - op)
        c = (ml - loc)/scale
        return triang.ppf(x, c, loc, scale)


def simulate_tasks_duration(project_graph):
    # Esta funcion el grafo con n tareas, cada cual con sus parametros de la 
    # correspondiente distribucion triangular, y devuelve una lista de 
    # n elementos, donde la posicion i corresponde a la duracion de la i-esima
    # tarea.
    # Sugerencia: recordar que la distribucion de la tarea i se encuentra en el 
    # diccionario project_graph.d[i]

    tasks_times = []
    for task in range(project_graph.get_n_tasks()):
        op,ml,ps = project_graph.get_tasks_dist_params()[task]
        tasks_times.append(simulate_triangular(op,ml,ps))
    return tasks_times

def get_path_duration(path, tasks_times):
    # Dado un camino, representado por path y la secuencia de tareas, y la
    # duracion de cada tarea (donde tasks_times[i] es la duracion de la i-esima
    # tarea, la funcion devuelve la duracion del camino dados esos tiempos.
    
    duration = 0
    for task in path:
        duration += tasks_times[task]
    return duration

def get_project_duration(project_graph, tasks_times):
    # La duracion del proyecto corresponde al maximo de las duraciones de los caminos.
    # Recordatorio: los caminos se encuentran en project_graph.paths, y se pueden
    # obtener con el proyecto get_paths()

    # La funcion debe computar la duracion de cada uno de los caminos y retornar el maximo.
    
    paths_durations = []
    for path in project_graph.get_paths():
        paths_durations.append(get_path_duration(path, tasks_times))
    
    return np.max(paths_durations)

def simulate(n_sim,project_graph):
    # Esta funcion realiza n_sim simulaciones y analiza los resultados necesarios para el
    # arbol de decision.
    # Idealmente, puede devolver una lista con la duracion para cada una de las
    # simulaciones para su posterior analisis.
    
    weeks = []
    for sim in range(n_sim):
        tasks_times = simulate_tasks_duration(project_graph)
        weeks.append(get_project_duration(project_graph, tasks_times))
        
    return weeks

def get_prob_in_range(vals, a, b):
    # Funcion auxiliar para analisis de resultados y calculo de probabilidades.
    # Dada una muestra de valores vals, calcula la proporcion de x in vals tales que 
    # a < x <= b.
    
    vals = np.array(vals)
    return round(sum((vals > a) & (vals <= b)) / len(vals),3) * 100
    

def main():

    # Fijamos la cantidad de simulaciones
    n_sim = 1000
    
    # Fijamos la semilla, por reproducibilidad.
    random.seed(0)

    # 300k por perder el deadline. Por ahora, 46.0
    # 150k por terminar en 40 o menos. Por ahora, mantenemos 40.0
    # Estos son los limites que nos importan.
    deadline = 47.0
    incentive = 40.0

    # Primer paso: consideramos el escenario sin contrataciones extra.
    graph_no_hire = ProjectGraph()

    # Simulamos en este contexto!
    results_no_hire = simulate(n_sim,graph_no_hire)
    
    # Analizamos los resultados.
    
    probIncentive = get_prob_in_range(results_no_hire, 0, incentive)
    probStandard = get_prob_in_range(results_no_hire, incentive, deadline)
    probDeadline = get_prob_in_range(results_no_hire, deadline, max(results_no_hire))
    
    plt.close()
    my_circle=plt.Circle( (0,0), 0.7, color='white')
    plt.pie([probIncentive, probStandard, probDeadline], 
            labels = ["Menos de 40 Semanas\n{}%".format(round(probIncentive, 3)), 
                      "Entre 40 y 47 Semanas\n{}%".format(round(probStandard,3)), 
                      "Mas de 47 Semanas\n{}%".format(round(probDeadline,3))], 
            colors=['green','orange','red'])
    plt.title("Resultados sin contratación")
    p=plt.gcf()
    p.gca().add_artist(my_circle)
    plt.savefig("Results no hire.png")
    
    # Segundo paso: analizar en el contexto que se hace la contratacion.
    # Esto lo representamos modifiando la duracion de las tarea 2.
    graph_hire = graph_no_hire
    graph_hire.dist_params[2] = (6.0, 9.0, 13.0)

    # Simulamos en este contexto!
    results_hire = simulate(n_sim,graph_hire)
    
    # Analizamos los resultados.

    probIncentive = get_prob_in_range(results_hire, 0, incentive)
    probStandard = get_prob_in_range(results_hire, incentive, deadline)
    probDeadline = get_prob_in_range(results_hire, deadline, max(results_hire))
    
    plt.close()
    my_circle=plt.Circle( (0,0), 0.7, color='white')
    plt.pie([probIncentive, probStandard, probDeadline], 
            labels = ["Menos de 40 Semanas\n{}%".format(round(probIncentive,3)), 
                      "Entre 40 y 47 Semanas\n{}%".format(round(probStandard,3)), 
                      "Mas de 47 Semanas\n{}%".format(round(probDeadline,3))], 
            colors=['green','orange','red'])
    plt.title("Resultados con contratación")
    p=plt.gcf()
    p.gca().add_artist(my_circle)
    plt.savefig("Results hire.png")

if __name__ == "__main__":
    main()
