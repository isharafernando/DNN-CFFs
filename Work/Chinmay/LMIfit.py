# -*- coding: utf-8 -*-
"""kvaluechanges.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uC8rQlzyyNcqF3EDWiTHQPQgvVMzSq51
"""

import numpy as np
import pandas as pd

from BHDVCS_tf import DvcsData
from BHDVCS_tf import cffs_from_globalModel
from BHDVCS_tf import F2VsPhi as F2VsPhitf
import tensorflow as tf

import matplotlib
import matplotlib.pyplot as plt

import sys
from scipy.stats import chisquare

from model_utils import Models

data_file = 'BKM_pseudodata.csv'

df = pd.read_csv(data_file, dtype=np.float64)
df = df.rename(columns={"sigmaF": "errF"})

# Changed splitting
def split_data(Kinematics,output,split=0.1):
  temp =np.random.choice(list(range(len(output))), size=int(len(output)*split), replace = False)

  test_X = pd.DataFrame.from_dict({k: v[temp] for k,v in Kinematics.items()})
  train_X = pd.DataFrame.from_dict({k: v.drop(temp) for k,v in Kinematics.items()})

  test_y = output[temp]
  train_y = output.drop(temp)

  return train_X, test_X, train_y, test_y

trainKin, testKin, trainOut, testOut = split_data(df[['phi_x', 'k', 'QQ', 'x_b', 't', 'F1', 'F2', 'dvcs']],df['F'],split =0.1)

models = Models()

early_stopping_callback = tf.keras.callbacks.EarlyStopping(monitor='loss', min_delta=0.0000005, patience=100)

tfModel = models.tf_model1(len(trainKin[["QQ","x_b","t","phi_x","k"]]))
Wsave = tfModel.get_weights()
tfModel.set_weights(Wsave)

tfModel.fit(trainKin[["QQ","x_b","t", "phi_x", "k"]], trainOut,
            epochs=50, verbose=1, batch_size=16, callbacks=[early_stopping_callback],
            validation_data=(testKin[["QQ","x_b","t", "phi_x", "k"]], testOut)) # validation loss

tfModel.save('cffs_model.h5') # saves model to .h5

# cffs = cffs_from_globalModel(tfModel, trainKin[["QQ","x_b","t", "phi_x", "k"]], numHL=2)

# df = pd.DataFrame(cffs)

# if len(sys.argv) > 1:
#     df.to_csv('bySetCFFs' + sys.argv[1] + '.csv')
# else:
#     df.to_csv('bySetCFFs.csv')

# displays results for train/validation loss
plt.plot(tfModel.history.history['loss'])
plt.plot(tfModel.history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper right')
plt.savefig('sample_BKM.png')
plt.show()