from sklearn.cluster                                    import KMeans
from sklearn.metrics                                    import pairwise_distances_argmin_min
from signlanguage.interfaces.interfaces_model                        import IKmeans, INeural
from tensorflow.keras.models                            import Sequential
from tensorflow.keras.layers                            import Dense
import numpy                                            as np


## core dispertion - single core
class CorePool(IKmeans):
    def __init__(self, n_clusters=4, max_iter=3000, init='k-means++'):
        #configuration
        self.n_clusters = n_clusters
        self._max_iter = max_iter if max_iter < 3000 else 3000
        self._init = init
        #evaluation meassure
        self.range_threshold = 0.01
        #core attr
        self.kmeans = KMeans(n_clusters=self.n_clusters, init=self._init, n_init='auto')#max_iter=self._max_iter, n_init='auto')
        self.cluster_centers_ = None

    def fit(self, X):
        try:
            self.kmeans.fit(X)
            self.cluster_centers_ = self.kmeans.cluster_centers_

        except Exception as e:
            print("Error Ocurrido [Core - Kmeans model], Mensaje: {0}".format(str(e)))

    def predict(self, X):
        try:
            distances = self.kmeans.transform(X)
            closest_cluster_distance = np.min(distances, axis=1)
            return 1 if (closest_cluster_distance[0] <= self.range_threshold and closest_cluster_distance[0] >= 0) else 0
        except Exception as e:
            print("Error Ocurrido [Core - Kmeans model - Predict], Mensaje: {0}".format(str(e)))
            return None
    
    def predict_cluster(self, X):
        return self.kmeans.predict(X)
    
    
    def predict_min(self, X):
        try:
            cluster_asignado = self.kmeans.predict(X)
            distances = pairwise_distances_argmin_min(X, self.cluster_centers_)[1]
            distancia_al_centroide = np.linalg.norm(X - self.cluster_centers_[cluster_asignado])
            return 1 if (distancia_al_centroide <= self.range_threshold and distancia_al_centroide >= 0) else 0
        except Exception as e:
            print("Error Ocurrido [Core - Kmeans model - PredictV2], Mensaje: {0}".format(str(e)))
            return None

## core classification - single core
class CoreClass(INeural):
    def __init__(self, neurals_count=30, dim_values=1, epochs=None):
        #core attr
        self.NeuralModel =None
        #configuration
        self.__dim_values= dim_values
        self.__neurals_ct = neurals_count
        self.__neural_denseLvl1 = round(self.__neurals_ct*0.5)        #depend of neurals_count --> qty data get (50% amount data)
        self.__neural_denseLvl2 = round(self.__neural_denseLvl1*0.5)  #depend of neurals_count --> qty data get (50% of lvl1)
        self.__neural_denseLvl3 = 1                                   #binomial classification neuron
        self.__epochs_itr = 1500 if epochs is None else epochs#self.__neurals_ct*10 if epochs is None else epochs
        self.__batch_sz   = 2**round(self.__neurals_ct*0.1)
        #evaluation meassure
        self.range_threshold = 0.90


    def fit(self, X, Y):
        try:
            self.NeuralModel.fit(X, Y, epochs=self.__epochs_itr, batch_size=self.__batch_sz)
            loss, accuracy =  self.NeuralModel.evaluate(X, Y)
            print(f"Pérdida: {loss}, Precisión: {accuracy}")
        except Exception as e:
            print("Error Ocurrido [Core - Neural model - Fit], Mensaje: {0}".format(str(e)))

    def predict(self, X):
        try:
            prediction = self.NeuralModel.predict(X)
            return [prediction > self.range_threshold, prediction]
        except Exception as e:
            print("Error Ocurrido [Core - Neural model - Predict], Mensaje: {0}".format(str(e)))
            return None
    
    def compile(self):
        try:
            #construction model view
            self.NeuralModel = Sequential([
                Dense(self.__neural_denseLvl1, activation='relu', input_dim=self.__dim_values), #representative learning
                Dense(self.__neural_denseLvl2, activation='relu'),   #complex learning
                Dense(self.__neural_denseLvl3, activation='sigmoid') #binomial clasifier
            ])
            self.NeuralModel.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        except Exception as e:
            print("Error Ocurrido [Core - Neural model - Compile], Mensaje: {0}".format(str(e)))
    
