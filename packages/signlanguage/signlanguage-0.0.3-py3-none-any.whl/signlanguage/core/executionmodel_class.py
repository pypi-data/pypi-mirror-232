from signlanguage.interfaces.interfaces_model    import Imodel
import signlanguage.models.handmodel_class       as hm
import numpy                        as np
import pandas                       as pd


class ExecutionModelPool(Imodel):
    def transform_dataEvaluation(self, data_model=None):
        if data_model is None:
            return None
        
        data_evaluation = [[] for _ in range(54)]
        for i, value in enumerate(data_model):
            if len(value) > 0:
                if not len(data_evaluation[i]) == len(value):
                    data_evaluation[i] = [[] for _ in range(len(value))]

                for j, val_pos in enumerate(value):
                    data_evaluation[i][j].extend([val_pos])
        
        return data_evaluation
    

    def evaluation(self, model_evaluation=None, data=None, face_relation=False, body_relation=False, hand_relation=False, hand_diff_relation=False):
        try:
            if None in (model_evaluation, data):
                return None
            
            results = None
            ##evaluation_model
            if not (face_relation or body_relation):
                results = self.hand_evaluation(model_evaluation=model_evaluation, data=data, face_relation=face_relation, body_relation=body_relation, hand_relation=hand_relation, hand_diff_relation=hand_diff_relation)         

            elif face_relation and not body_relation:
                results = self.face_evaluation(model_evaluation=model_evaluation, data=data, face_relation=face_relation, body_relation=body_relation, hand_relation=hand_relation, hand_diff_relation=hand_diff_relation)         
            
            elif body_relation:
                results = self.body_evaluation(model_evaluation=model_evaluation, data=data, face_relation=face_relation, body_relation=body_relation, hand_relation=hand_relation, hand_diff_relation=hand_diff_relation)
            ##results_recog
            return results
            
        except Exception as e:
            print("Error Ocurrido [Model Exec], Mensaje: {0}".format(str(e)))
            return None
        
    ## Evalua los puntos de interseccion del cuerpo en general
    def body_evaluation(self, model_evaluation=None, data=None, face_relation=False, body_relation=False, hand_relation=False, hand_diff_relation=False):
        if None in (model_evaluation, data) or not body_relation:
            return None
        
        matrix_evaluation = self.hand_evaluation(model_evaluation=model_evaluation, data=data, face_relation=face_relation, body_relation=body_relation, hand_relation=hand_relation)

        if matrix_evaluation is None or len(matrix_evaluation) != 54:
            return None
        
        #construct model data evaluation
        data_model = hm.HandModel().make_model(hand_Left=data['model_hand_Left'], hand_Right=data['model_hand_Right'], points_body=data['model_body'], face_relation=face_relation, body_relation=body_relation, hand_relation=hand_relation, hand_diff_relation=hand_diff_relation)
        
        #pre evaluation model, defined
        defined_index = {i for i, model in enumerate(model_evaluation) if len(model) > 0}

        #transform data evaluation
        data_evaluation = self.transform_dataEvaluation(data_model=data_model)

        ## array index -> [15, 16, 17, 18, 19, 20]
        defined_values = {15, 16, 17, 18, 19, 20}
        defined_intersection = sorted(list(defined_index.intersection(defined_values)))

        if len(defined_intersection) == 6:
            
            #15 handRightX --------------------------------------------------------------
            evaluation_data  = data_evaluation[15]
            evaluation_model = model_evaluation[15]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[15].append(result_value)


            #16 handRightX --------------------------------------------------------------
            evaluation_data  = data_evaluation[16]
            evaluation_model = model_evaluation[16]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[16].append(result_value)

            #17 handRightX --------------------------------------------------------------
            evaluation_data  = data_evaluation[17]
            evaluation_model = model_evaluation[17]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[17].append(result_value)


            #18 handLeftX --------------------------------------------------------------
            evaluation_data  = data_evaluation[18]
            evaluation_model = model_evaluation[18]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[18].append(result_value)


            #19 handLeftX --------------------------------------------------------------
            evaluation_data  = data_evaluation[19]
            evaluation_model = model_evaluation[19]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[19].append(result_value)

            #20 handLeftX --------------------------------------------------------------
            evaluation_data  = data_evaluation[20]
            evaluation_model = model_evaluation[20]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[20].append(result_value)

        else:
            if defined_intersection == [15, 16, 17]:
                #15 handRightX --------------------------------------------------------------
                evaluation_data  = data_evaluation[15]
                evaluation_model = model_evaluation[15]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[15].append(result_value)


                #16 handRightX --------------------------------------------------------------
                evaluation_data  = data_evaluation[16]
                evaluation_model = model_evaluation[16]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[16].append(result_value)

                #17 handRightX --------------------------------------------------------------
                evaluation_data  = data_evaluation[17]
                evaluation_model = model_evaluation[17]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[17].append(result_value)
            
            elif defined_intersection == [18, 19, 20]:
                #18 handLeftX --------------------------------------------------------------
                evaluation_data  = data_evaluation[18]
                evaluation_model = model_evaluation[18]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[18].append(result_value)


                #19 handLeftX --------------------------------------------------------------
                evaluation_data  = data_evaluation[19]
                evaluation_model = model_evaluation[19]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[19].append(result_value)

                #20 handLeftX --------------------------------------------------------------
                evaluation_data  = data_evaluation[20]
                evaluation_model = model_evaluation[20]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[20].append(result_value)
    
            else:
                return None
            
        if hand_relation:
            ## array index -> [12, 13, 14]
            defined_values = {12, 13, 14}
            defined_intersection = sorted(list(defined_index.intersection(defined_values)))

            if len(defined_intersection) == 3:
                #12 X --------------------------------------------------------------
                evaluation_data  = data_evaluation[12]
                evaluation_model = model_evaluation[12]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[12].append(result_value)


                #13 Y --------------------------------------------------------------
                evaluation_data  = data_evaluation[13]
                evaluation_model = model_evaluation[13]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[13].append(result_value)

                #14 Z --------------------------------------------------------------
                evaluation_data  = data_evaluation[14]
                evaluation_model = model_evaluation[14]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[14].append(result_value)

            else:
                return None
            
        if hand_diff_relation:
            ## array index -> [21, 22, 23, 24, 25, 26]
            defined_values = {21, 22, 23, 24, 25, 26}
            defined_intersection = sorted(list(defined_index.intersection(defined_values)))
            
            if len(defined_intersection) == 6:
                #21 handRightX --------------------------------------------------------------
                evaluation_data  = data_evaluation[21]
                evaluation_model = model_evaluation[21]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[21].append(result_value)


                #22 handRightY --------------------------------------------------------------
                evaluation_data  = data_evaluation[22]
                evaluation_model = model_evaluation[22]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[22].append(result_value)

                #23 handRightZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[23]
                evaluation_model = model_evaluation[23]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[23].append(result_value)


                #24 handLeftX --------------------------------------------------------------
                evaluation_data  = data_evaluation[24]
                evaluation_model = model_evaluation[24]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[24].append(result_value)


                #25 handLeftY --------------------------------------------------------------
                evaluation_data  = data_evaluation[25]
                evaluation_model = model_evaluation[25]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[25].append(result_value)

                #26 handLeftZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[26]
                evaluation_model = model_evaluation[26]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[26].append(result_value)

            else:
                if defined_intersection == [21, 22, 23]:
                    #21 handRightX --------------------------------------------------------------
                    evaluation_data  = data_evaluation[21]
                    evaluation_model = model_evaluation[21]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[21].append(result_value)


                    #22 handRightY --------------------------------------------------------------
                    evaluation_data  = data_evaluation[22]
                    evaluation_model = model_evaluation[22]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[22].append(result_value)

                    #23 handRightZ --------------------------------------------------------------
                    evaluation_data  = data_evaluation[23]
                    evaluation_model = model_evaluation[23]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[23].append(result_value)
                
                elif defined_intersection == [24, 25, 26]:
                    #24 handLeftX --------------------------------------------------------------
                    evaluation_data  = data_evaluation[24]
                    evaluation_model = model_evaluation[24]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[24].append(result_value)


                    #25 handLeftY --------------------------------------------------------------
                    evaluation_data  = data_evaluation[25]
                    evaluation_model = model_evaluation[25]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[25].append(result_value)

                    #26 handLeftZ --------------------------------------------------------------
                    evaluation_data  = data_evaluation[26]
                    evaluation_model = model_evaluation[26]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[26].append(result_value)
                
                else:
                    return None
                
        if face_relation:
            ## array index -> [27, 28, 29, 30, 31, 32]
            defined_values = {27, 28, 29, 30, 31, 32}
            defined_intersection = sorted(list(defined_index.intersection(defined_values)))

            if len(defined_intersection) == 6:
                #27 handRightX --------------------------------------------------------------
                evaluation_data  = data_evaluation[27]
                evaluation_model = model_evaluation[27]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[27].append(result_value)


                #28 handRightY --------------------------------------------------------------
                evaluation_data  = data_evaluation[28]
                evaluation_model = model_evaluation[28]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[28].append(result_value)

                #29 handRightZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[29]
                evaluation_model = model_evaluation[29]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[29].append(result_value)


                #30 handLeftX --------------------------------------------------------------
                evaluation_data  = data_evaluation[30]
                evaluation_model = model_evaluation[30]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[30].append(result_value)


                #31 handLeftY --------------------------------------------------------------
                evaluation_data  = data_evaluation[31]
                evaluation_model = model_evaluation[31]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[31].append(result_value)

                #32 handLeftZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[32]
                evaluation_model = model_evaluation[32]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[32].append(result_value)

            else:
                if defined_intersection == [27, 28, 29]:
                    #27 handRightX --------------------------------------------------------------
                    evaluation_data  = data_evaluation[27]
                    evaluation_model = model_evaluation[27]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[27].append(result_value)


                    #28 handRightY --------------------------------------------------------------
                    evaluation_data  = data_evaluation[28]
                    evaluation_model = model_evaluation[28]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[28].append(result_value)

                    #29 handRightZ --------------------------------------------------------------
                    evaluation_data  = data_evaluation[29]
                    evaluation_model = model_evaluation[29]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[29].append(result_value)
                
                elif defined_intersection == [30, 31, 32]:
                    #30 handLeftX --------------------------------------------------------------
                    evaluation_data  = data_evaluation[30]
                    evaluation_model = model_evaluation[30]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[30].append(result_value)


                    #31 handLeftY --------------------------------------------------------------
                    evaluation_data  = data_evaluation[31]
                    evaluation_model = model_evaluation[31]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[31].append(result_value)

                    #32 handLeftZ --------------------------------------------------------------
                    evaluation_data  = data_evaluation[32]
                    evaluation_model = model_evaluation[32]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[32].append(result_value)

                else:
                    return None
            
            if hand_diff_relation:
                ## array index -> [33, 34, 35, 36, 37, 38]
                defined_values = {33, 34, 35, 36, 37, 38}
                defined_intersection = sorted(list(defined_index.intersection(defined_values)))

                if len(defined_intersection) == 6:
                    #33 handRightX --------------------------------------------------------------
                    evaluation_data  = data_evaluation[33]
                    evaluation_model = model_evaluation[33]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[33].append(result_value)


                    #34 handRightY --------------------------------------------------------------
                    evaluation_data  = data_evaluation[34]
                    evaluation_model = model_evaluation[34]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[34].append(result_value)

                    #35 handRightZ --------------------------------------------------------------
                    evaluation_data  = data_evaluation[35]
                    evaluation_model = model_evaluation[35]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[35].append(result_value)


                    #36 handLeftX --------------------------------------------------------------
                    evaluation_data  = data_evaluation[36]
                    evaluation_model = model_evaluation[36]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[36].append(result_value)


                    #37 handLeftY --------------------------------------------------------------
                    evaluation_data  = data_evaluation[37]
                    evaluation_model = model_evaluation[37]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[37].append(result_value)

                    #38 handLeftZ --------------------------------------------------------------
                    evaluation_data  = data_evaluation[38]
                    evaluation_model = model_evaluation[38]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[38].append(result_value)

                else:
                    if defined_intersection[33, 34, 35]:
                        #33 handRightX --------------------------------------------------------------
                        evaluation_data  = data_evaluation[33]
                        evaluation_model = model_evaluation[33]

                        for i, evaluation_pos in enumerate(evaluation_data):
                            if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                                return None
                            
                            #configure values
                            data = np.array(evaluation_pos).T
                            df_real = pd.DataFrame(data).transpose()

                            #get core pool
                            result_value = evaluation_model[i].predict_min(df_real)
                            matrix_evaluation[33].append(result_value)


                        #34 handRightY --------------------------------------------------------------
                        evaluation_data  = data_evaluation[34]
                        evaluation_model = model_evaluation[34]

                        for i, evaluation_pos in enumerate(evaluation_data):
                            if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                                return None
                            
                            #configure values
                            data = np.array(evaluation_pos).T
                            df_real = pd.DataFrame(data).transpose()

                            #get core pool
                            result_value = evaluation_model[i].predict_min(df_real)
                            matrix_evaluation[34].append(result_value)

                        #35 handRightZ --------------------------------------------------------------
                        evaluation_data  = data_evaluation[35]
                        evaluation_model = model_evaluation[35]

                        for i, evaluation_pos in enumerate(evaluation_data):
                            if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                                return None
                            
                            #configure values
                            data = np.array(evaluation_pos).T
                            df_real = pd.DataFrame(data).transpose()

                            #get core pool
                            result_value = evaluation_model[i].predict_min(df_real)
                            matrix_evaluation[35].append(result_value)
                    
                    elif defined_intersection == [36, 37, 38]:
                        #36 handLeftX --------------------------------------------------------------
                        evaluation_data  = data_evaluation[36]
                        evaluation_model = model_evaluation[36]

                        for i, evaluation_pos in enumerate(evaluation_data):
                            if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                                return None
                            
                            #configure values
                            data = np.array(evaluation_pos).T
                            df_real = pd.DataFrame(data).transpose()

                            #get core pool
                            result_value = evaluation_model[i].predict_min(df_real)
                            matrix_evaluation[36].append(result_value)


                        #37 handLeftY --------------------------------------------------------------
                        evaluation_data  = data_evaluation[37]
                        evaluation_model = model_evaluation[37]

                        for i, evaluation_pos in enumerate(evaluation_data):
                            if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                                return None
                            
                            #configure values
                            data = np.array(evaluation_pos).T
                            df_real = pd.DataFrame(data).transpose()

                            #get core pool
                            result_value = evaluation_model[i].predict_min(df_real)
                            matrix_evaluation[37].append(result_value)

                        #38 handLeftZ --------------------------------------------------------------
                        evaluation_data  = data_evaluation[38]
                        evaluation_model = model_evaluation[38]

                        for i, evaluation_pos in enumerate(evaluation_data):
                            if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                                return None
                            
                            #configure values
                            data = np.array(evaluation_pos).T
                            df_real = pd.DataFrame(data).transpose()

                            #get core pool
                            result_value = evaluation_model[i].predict_min(df_real)
                            matrix_evaluation[38].append(result_value)

                    else:
                        return None
            
        return matrix_evaluation
    
    ## Evalua los puntos de interseccion de la cara-mano especificos, para reconocer relaciones definidas
    def face_evaluation(self, model_evaluation=None, data=None, face_relation=False, body_relation=False, hand_relation=False, hand_diff_relation=False):
        
        if None in (model_evaluation, data) or not face_relation:
            return None
        
        # evaluate hand vals
        matrix_evaluation = self.hand_evaluation(model_evaluation=model_evaluation, data=data, face_relation=face_relation, body_relation=body_relation, hand_relation=hand_relation)

        if matrix_evaluation is None or len(matrix_evaluation) != 54:
            return None
        
        #construct model data evaluation
        data_model = hm.HandModel().make_model(hand_Left=data['model_hand_Left'], hand_Right=data['model_hand_Right'], points_body=data['model_body'], face_relation=face_relation, body_relation=body_relation, hand_relation=hand_relation, hand_diff_relation=hand_diff_relation)
        
        #pre evaluation model, defined
        defined_index = {i for i, model in enumerate(model_evaluation) if len(model) > 0}

        #transform data evaluation
        data_evaluation = self.transform_dataEvaluation(data_model=data_model)

        ## array index -> [39, 40, 41, 42, 43, 44]
        defined_values = {39, 40, 41, 42, 43, 44}
        defined_intersection = sorted(list(defined_index.intersection(defined_values)))
        
        if len(defined_intersection) == 6:
            
            #42 handRightX --------------------------------------------------------------
            evaluation_data  = data_evaluation[39]
            evaluation_model = model_evaluation[39]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[39].append(result_value)
            
            #43 handRightY --------------------------------------------------------------
            evaluation_data  = data_evaluation[40]
            evaluation_model = model_evaluation[40]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[40].append(result_value)

            #44 handRightZ --------------------------------------------------------------
            evaluation_data  = data_evaluation[41]
            evaluation_model = model_evaluation[41]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[41].append(result_value)

            #45 handLefttX --------------------------------------------------------------
            evaluation_data  = data_evaluation[42]
            evaluation_model = model_evaluation[42]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[42].append(result_value)
            
            #46 handLeftY --------------------------------------------------------------
            evaluation_data  = data_evaluation[43]
            evaluation_model = model_evaluation[43]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[43].append(result_value)

            #47 handLeftZ --------------------------------------------------------------
            evaluation_data  = data_evaluation[44]
            evaluation_model = model_evaluation[44]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[44].append(result_value)

            return matrix_evaluation
        
        elif len(defined_intersection) == 3:
            
            if defined_intersection == [39, 40, 41]:
                
                #42 handRightX --------------------------------------------------------------
                evaluation_data  = data_evaluation[39]
                evaluation_model = model_evaluation[39]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[39].append(result_value)
                
                #43 handRightY --------------------------------------------------------------
                evaluation_data  = data_evaluation[40]
                evaluation_model = model_evaluation[40]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[40].append(result_value)

                #44 handRightZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[41]
                evaluation_model = model_evaluation[41]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[41].append(result_value)
                
            elif defined_intersection == [42, 43, 44]:
                
                #45 handLefttX --------------------------------------------------------------
                evaluation_data  = data_evaluation[42]
                evaluation_model = model_evaluation[42]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[42].append(result_value)
                
                #46 handLeftY --------------------------------------------------------------
                evaluation_data  = data_evaluation[43]
                evaluation_model = model_evaluation[43]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[43].append(result_value)

                #47 handLeftZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[44]
                evaluation_model = model_evaluation[44]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[44].append(result_value)

            else:
                return None
            
        if hand_diff_relation:
            
            ## array index -> [48, 49, 50, 51, 52, 53]
            defined_values = {48, 49, 50, 51, 52, 53}
            defined_intersection = sorted(list(defined_index.intersection(defined_values)))

            if len(defined_intersection) == 6:
                
                #48 handRightX --------------------------------------------------------------
                evaluation_data  = data_evaluation[48]
                evaluation_model = model_evaluation[48]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[48].append(result_value)
                
                #49 handRightY --------------------------------------------------------------
                evaluation_data  = data_evaluation[49]
                evaluation_model = model_evaluation[49]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[49].append(result_value)

                #50 handRightZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[50]
                evaluation_model = model_evaluation[50]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[50].append(result_value)

                #51 handLefttX --------------------------------------------------------------
                evaluation_data  = data_evaluation[51]
                evaluation_model = model_evaluation[51]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[51].append(result_value)
                
                #52 handLeftY --------------------------------------------------------------
                evaluation_data  = data_evaluation[52]
                evaluation_model = model_evaluation[52]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[52].append(result_value)

                #53 handLeftZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[53]
                evaluation_model = model_evaluation[53]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[53].append(result_value)
            
            elif len(defined_intersection) == 3:
                
                if defined_intersection == [48, 49, 50,]:
                    
                    #48 handRightX --------------------------------------------------------------
                    evaluation_data  = data_evaluation[48]
                    evaluation_model = model_evaluation[48]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[48].append(result_value)
                    
                    #49 handRightY --------------------------------------------------------------
                    evaluation_data  = data_evaluation[49]
                    evaluation_model = model_evaluation[49]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[49].append(result_value)

                    #50 handRightZ --------------------------------------------------------------
                    evaluation_data  = data_evaluation[50]
                    evaluation_model = model_evaluation[50]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[50].append(result_value)
                    
                elif defined_intersection == [51, 52, 53]:
                    
                    #51 handLefttX --------------------------------------------------------------
                    evaluation_data  = data_evaluation[51]
                    evaluation_model = model_evaluation[51]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[51].append(result_value)
                    
                    #52 handLeftY --------------------------------------------------------------
                    evaluation_data  = data_evaluation[52]
                    evaluation_model = model_evaluation[52]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[52].append(result_value)

                    #53 handLeftZ --------------------------------------------------------------
                    evaluation_data  = data_evaluation[53]
                    evaluation_model = model_evaluation[53]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[53].append(result_value)

                else:
                    return None
            
            else: 
                return None

        return matrix_evaluation
        
    ## Evalua los puntos de interseccion de las manos especificas, para reconocer unicamente movimiento de mano
    def hand_evaluation(self, model_evaluation=None, data=None, face_relation=False, body_relation=False, hand_relation=False, hand_diff_relation=False):

        if None in (model_evaluation, data):
            return None

        matrix_evaluation = [[] for _ in range(54)]

        #construct model data evaluation
        data_model = hm.HandModel().make_model(hand_Left=data['model_hand_Left'], hand_Right=data['model_hand_Right'], points_body=data['model_body'], face_relation=face_relation, body_relation=body_relation, hand_relation=hand_relation, hand_diff_relation=hand_diff_relation)
        
        #pre evaluation model, defined
        defined_index = {i for i, model in enumerate(model_evaluation) if len(model) > 0}
        
        ## array index -> [3,4,5,6,7,8]
        defined_values = {3, 4, 5, 6, 7, 8}
        defined_intersection = sorted(list(defined_index.intersection(defined_values)))

        #transform data evaluation
        data_evaluation = self.transform_dataEvaluation(data_model=data_model)
            
        if len(defined_intersection) == 6:

            #3 handRightX --------------------------------------------------------------
            evaluation_data  = data_evaluation[3]
            evaluation_model = model_evaluation[3]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[3].append(result_value)
            
            #4 handRightY --------------------------------------------------------------
            evaluation_data  = data_evaluation[4]
            evaluation_model = model_evaluation[4]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[4].append(result_value)

            #5 handRightZ --------------------------------------------------------------
            evaluation_data  = data_evaluation[5]
            evaluation_model = model_evaluation[5]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[5].append(result_value)

            #6 handLefttX --------------------------------------------------------------
            evaluation_data  = data_evaluation[6]
            evaluation_model = model_evaluation[6]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[6].append(result_value)
            
            #7 handLeftY --------------------------------------------------------------
            evaluation_data  = data_evaluation[7]
            evaluation_model = model_evaluation[7]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[7].append(result_value)

            #8 handLeftZ --------------------------------------------------------------
            evaluation_data  = data_evaluation[8]
            evaluation_model = model_evaluation[8]

            for i, evaluation_pos in enumerate(evaluation_data):
                if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                    return None
                
                #configure values
                data = np.array(evaluation_pos).T
                df_real = pd.DataFrame(data).transpose()

                #get core pool
                result_value = evaluation_model[i].predict_min(df_real)
                matrix_evaluation[8].append(result_value)
        
        else:
            
            if defined_intersection == [3,4,5]:
                
                #3 handRightX --------------------------------------------------------------
                evaluation_data  = data_evaluation[3]
                evaluation_model = model_evaluation[3]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[3].append(result_value)
                #4 handRightY --------------------------------------------------------------
                evaluation_data  = data_evaluation[4]
                evaluation_model = model_evaluation[4]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[4].append(result_value)

                #5 handRightZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[5]
                evaluation_model = model_evaluation[5]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[5].append(result_value)

            elif defined_intersection == [6,7,8]:
                
                #6 handLefttX --------------------------------------------------------------
                evaluation_data  = data_evaluation[6]
                evaluation_model = model_evaluation[6]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[6].append(result_value)
                
                #7 handLeftY --------------------------------------------------------------
                evaluation_data  = data_evaluation[7]
                evaluation_model = model_evaluation[7]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[7].append(result_value)

                #8 handLeftZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[8]
                evaluation_model = model_evaluation[8]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[8].append(result_value)
            
            else:
                return None

        if hand_relation:

            ## array index -> [0,1,2]
            defined_values = {0, 1, 2}
            defined_intersection = sorted(list(defined_index.intersection(defined_values)))

            if len(defined_intersection) == 3:

                #0 handX --------------------------------------------------------------
                evaluation_data  = data_evaluation[0]
                evaluation_model = model_evaluation[0]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[0].append(result_value)
                
                #1 handY --------------------------------------------------------------
                evaluation_data  = data_evaluation[1]
                evaluation_model = model_evaluation[1]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[1].append(result_value)

                #2 handZ --------------------------------------------------------------
                evaluation_data  = data_evaluation[2]
                evaluation_model = model_evaluation[2]

                for i, evaluation_pos in enumerate(evaluation_data):
                    if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                        return None
                    
                    #configure values
                    data = np.array(evaluation_pos).T
                    df_real = pd.DataFrame(data).transpose()

                    #get core pool
                    result_value = evaluation_model[i].predict_min(df_real)
                    matrix_evaluation[2].append(result_value)
            
            else:
                return None #no condition met

        """ #deprecated verified adaptation model
        if hand_diff_relation:

            ## array index -> [9, 10, 11]
            defined_values = {9, 10, 11}
            defined_intersection = sorted(list(defined_index.intersection(defined_values)))

            if len(defined_intersection) == 3 and defined_intersection == [9, 10, 11]:

                    #9 handRightX --------------------------------------------------------------
                    evaluation_data  = data_evaluation[9]
                    evaluation_model = model_evaluation[9]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[9].append(result_value)
                    
                    #10 handRightY --------------------------------------------------------------
                    evaluation_data  = data_evaluation[10]
                    evaluation_model = model_evaluation[10]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[10].append(result_value)

                    #11 handRightZ --------------------------------------------------------------
                    evaluation_data  = data_evaluation[11]
                    evaluation_model = model_evaluation[11]

                    for i, evaluation_pos in enumerate(evaluation_data):
                        if len(evaluation_pos) <= 0 and evaluation_model[i] is None:
                            return None
                        
                        #configure values
                        data = np.array(evaluation_pos).T
                        df_real = pd.DataFrame(data).transpose()

                        #get core pool
                        result_value = evaluation_model[i].predict_min(df_real)
                        matrix_evaluation[11].append(result_value)
                    
            else:
                return None #no condition met
        """
        
        return matrix_evaluation
    
class ExecutionModelMovement(Imodel):
    def transform_dataEvaluation(self, data_model=None):
        if data_model is None:
            return None
        
        data_evaluation = [[] for _ in range(6)]
           
        for i, value in enumerate(data_model):
            if len(value) > 0:
                if not len(data_evaluation[i]) == len(value):
                    data_evaluation[i] = [[] for _ in range(len(value))]
                
                for j, val_pos in enumerate(value):
                    data_evaluation[i][j].extend([val_pos])
        
        return data_evaluation
    
    def evaluation(self, model_evaluation=None, data=None):
        try:
            if None in (model_evaluation, data):
                    return None
            
            matrix_evaluation = [[] for _ in range(6)]

            data_model = hm.HandModel().make_model_body(hand_Left=data['model_hand_Left'], hand_Right=data['model_hand_Right'], points_body=data['model_body'])
        
            #pre evaluation model, defined
            defined_index = [i for i, model in enumerate(model_evaluation) if len(model) > 0]

            #transform data evaluation
            data_evaluation = self.transform_dataEvaluation(data_model=data_model)
            defined_evaluation = [i for i, model in enumerate(data_evaluation) if len(model) > 0]

            if len(defined_index) == len(defined_evaluation) and defined_evaluation == defined_index:                   
                    for i in defined_index:
                        if len(model_evaluation[i])>0:
                            evaluation_data  = data_evaluation[i]
                            evaluation_model = model_evaluation[i]

                            for j, evaluation_pos in enumerate(evaluation_data):
                                if len(evaluation_pos) <= 0 and evaluation_model[j] is None:
                                    return None
                                
                                #configure values
                                data = np.array(evaluation_pos).T
                                df_real = pd.DataFrame(data).transpose()

                                #get core pool
                                result_value = evaluation_model[j].predict_min(df_real)
                                matrix_evaluation[i].append(result_value)
                        else:
                            return None
                        
                    return matrix_evaluation
            return None
        except Exception as e:
            print("Error Ocurrido [Model Exec Movement], Mensaje: {0}".format(str(e)))
            return None
    
class ExecutionModelClassifier(Imodel):
     def evaluation(self, model_classification=None, data=None):
        try:
            if None in (model_classification, data):
                return None
            
            if len(model_classification)!=len(data):
                return None
            
            results = []
            
            defined_index = [i for i, model in enumerate(model_classification) if model is not None]

            for index_ in defined_index:
               results.append(model_classification[index_].predict(np.array([data[index_]]))) 
            
            ##results_recog
            return [all(item[0] for item in results), results]
            
        except Exception as e:
            print("Error Ocurrido [Model Exec - class], Mensaje: {0}".format(str(e)))
            return None

class ExecutionModelState(Imodel):
    def evaluation(self, model_classification=None, data=None):
        try:
            if None in (model_classification, data):
                return None          
            
            ##results_recog
            return model_classification.predict(np.array([data]))
            
        except Exception as e:
            print("Error Ocurrido [Model Exec - Movement State], Mensaje: {0}".format(str(e)))
            return None