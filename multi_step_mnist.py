from metaflow import FlowSpec, step, Parameter, IncludeFile, retry,conda_base
import struct


def parse_data(np,x_dataset, y_dataset, flatten):
    _, num = struct.unpack(">II", y_dataset[:8])
    labels = np.frombuffer(y_dataset[8:], dtype=np.int8) #int8
    new_labels = np.zeros((num, 10))
    new_labels[np.arange(num), labels] = 1
    _, num, rows, cols = struct.unpack(">IIII", x_dataset[:16])
    imgs = np.frombuffer(x_dataset[16:], dtype=np.uint8).reshape(num, rows, cols) #uint8
    imgs = imgs.astype(np.float32) / 255.0
    if flatten:
        imgs = imgs.reshape([num, -1])

    return imgs, new_labels


def read_mnist(np,train_x_raw,train_y_raw,test_x_raw,test_y_raw, flatten=True, num_train=55000):
    """
    Read in the mnist dataset, given that the data is stored in path
    Return two tuples of numpy arrays
    ((train_imgs, train_labels), (test_imgs, test_labels))
    """
    imgs, labels = parse_data(np,train_x_raw,train_y_raw, flatten)
    indices = np.random.permutation(labels.shape[0])
    train_idx, val_idx = indices[:num_train], indices[num_train:]
    train_img, train_labels = imgs[train_idx, :], labels[train_idx, :]
    val_img, val_labels = imgs[val_idx, :], labels[val_idx, :]
    test = parse_data(np,test_x_raw,test_y_raw, flatten)
    return (train_img, train_labels), (val_img, val_labels), test


def script_path(filename):
    """
    A convenience function to get the absolute path to a file in this
    tutorial's directory. This allows the tutorial to be launched from any
    directory.

    """
    import os

    filepath = os.path.join(os.path.dirname(__file__))
    return os.path.join(filepath, filename)


def get_python_version():
    """
    A convenience function to get the python version used to run this
    tutorial. This ensures that the conda environment is created with an
    available version of python.

    """
    import platform
    versions = {'2' : '2.7.15',
                '3' : '3.6.5'}
    return versions[platform.python_version_tuple()[0]]


# Uncomment below line to run it with Conda.
@conda_base(python=get_python_version(),libraries={'numpy':'1.18.1','tensorflow':'1.5.0','python-kubernetes':'10.0.1'})
class MultiStepMNISTFlow(FlowSpec):
    """
    Train multiple Iterations of Machine learning models for MNIST Handwritten digit prediction.
    Metaflow will help capture the experiments and then understanding the efficiency of training and accuracy for each of the models.

    """

    mnist_dataset_train_x_raw = IncludeFile("mnist_dataset_train_x_raw",
                             help="The path to a mnist training images file.",
                             default=script_path('data/mnist/train-images-idx3-ubyte'),is_text=False,encoding='UTF-8')
    
    mnist_dataset_train_y_raw = IncludeFile("mnist_dataset_train_y_raw",
                             help="The path to a  mnist training labels file.",
                             default=script_path('data/mnist/train-labels-idx1-ubyte'),is_text=False,encoding='UTF-8')

    mnist_dataset_test_x_raw = IncludeFile("mnist_dataset_test_x_raw",
                                 help="The path to a mnist test images file.",
                                 default=script_path('data/mnist/t10k-images-idx3-ubyte'),is_text=False,encoding='UTF-8')

    mnist_dataset_test_y_raw = IncludeFile("mnist_dataset_test_y_raw",
                             help="The path to a mnist test labels file.",
                             default=script_path('data/mnist/t10k-labels-idx1-ubyte'),is_text=False,encoding='UTF-8')

    num_training_examples = Parameter('num_training_examples',help='Number of Training Examples',default=5000)

    number_of_epochs = Parameter('number_of_epochs',help='Number of Epochs to Run for the Training Process',default=10)

    # batch_size = Parameter('batch_size',help='Batch Sizes for the Training Process',default=128)

    
    @step
    def start(self):
        """
        Parse the MNIST Dataset into Flattened and None Flattened Data artifacts. 
        Also set the hyper params to search over in the following steps. 
        """
        import numpy as np
        # $ Collect and create the unflattenned dataset according to the number of examples.
        self.train_unflattened,self.val_unflattened,self.test_unflattened = read_mnist(np,self.mnist_dataset_train_x_raw,self.mnist_dataset_train_y_raw,self.mnist_dataset_test_x_raw,self.mnist_dataset_test_y_raw,flatten=False,num_train=self.num_training_examples)
        
        # $ Collect and create the flattenned dataset according to the number of examples.
        self.train_flattened,self.val_flattened,self.test_flattened = read_mnist(np,self.mnist_dataset_train_x_raw,self.mnist_dataset_train_y_raw,self.mnist_dataset_test_x_raw,self.mnist_dataset_test_y_raw,flatten=True,num_train=self.num_training_examples)
        
        self.hyper_params =  list(map(lambda x:{'batch_size':x},[128,32,64])) # {batch_size : 100} .... 
        
        self.history = {}
        # $ Train models in parallel withe the 
        self.next(self.train_sequential_placeholder,self.train_convolution_placeholder,self.train_convolution_batch_norm_placeholder)

    @step
    def train_sequential_placeholder(self):
        """
        This a placeholder on the Sequential NN branched step to run a Foreach on the self.hyper_params 
        """
        self.next(self.train_sequential,foreach='hyper_params')

    @step
    def train_convolution_placeholder(self):
        """
        This a placeholder on the Convolution NN branched step to run a Foreach on the self.hyper_params 
        """
        self.next(self.train_convolution,foreach='hyper_params')
    
    @step
    def train_convolution_batch_norm_placeholder(self):
        """
        This a placeholder on the Convolution Batch Normalisation NN branched step to run a Foreach on the self.hyper_params 
        """
        self.next(self.train_convolution_batch_norm,foreach='hyper_params')

    @step
    def train_sequential(self):
        """
        Train sequential Neural Network with the input Hyper params
        
        """
        from tensorflow.python.keras.layers import Conv2D,Input,MaxPool2D,Dense,Flatten,MaxPooling2D
        from tensorflow.python.keras.models import Sequential
        train, val, test = self.train_flattened,self.val_flattened,self.test_flattened
        train_X,train_Y = train
        test_X,test_Y = test
        model = Sequential()
        model.add(Dense(128, activation='relu',input_shape=[784]))  # fully-connected layer with 128 units and ReLU activation
        model.add(Dense(128, activation='relu'))
        model.add(Dense(10, activation='softmax'))  # output layer with 10 units and a softmax activation

        model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['categorical_accuracy','accuracy'])
        history = model.fit(train_X,train_Y, validation_split=0.2, epochs=self.number_of_epochs, batch_size=self.input['batch_size'])
        self.history = dict(history.history)
        self.param = self.input
        self.next(self.train_sequential_join)

    @step
    def train_convolution(self):
        """
        Train a Convolutional Neural Network with the input Hyper params. 
        """
        from tensorflow.python.keras.layers import Conv2D,Input,MaxPool2D,Dense,Flatten,MaxPooling2D
        from tensorflow.python.keras.models import Sequential
        train, val, test = self.train_unflattened,self.val_unflattened,self.test_unflattened
        train_X,train_Y = train
        test_X,test_Y = test
        train_X = train_X.reshape(self.num_training_examples,28,28,1)
        test_X = test_X.reshape(test_X.shape[0],28,28,1)
        model = Sequential()
        model.add(Conv2D(32,kernel_size=(1,1),activation='relu',input_shape=(28,28,1)))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64,kernel_size=(3,3),activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128,kernel_size=(3,3),activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))  
        model.add(Dense(10, activation='softmax'))
        model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['categorical_accuracy','accuracy'])
        history = model.fit(train_X,train_Y, validation_split=0.2, epochs=self.number_of_epochs, batch_size=self.input['batch_size'])
        self.history = dict(history.history)
        self.param = self.input
        self.next(self.train_convolution_join)

    
    @step
    def train_convolution_batch_norm(self):
        """
        Train a Convolutional Neural Network with Batch Norm and Dropout with the input Hyper params. 
        """
        from tensorflow.python.keras.layers import Conv2D,Input,MaxPool2D,Dense,Flatten,MaxPooling2D,BatchNormalization,Activation,Dropout
        from tensorflow.python.keras.models import Sequential
        train, val, test = self.train_unflattened,self.val_unflattened,self.test_unflattened
        train_X,train_Y = train
        test_X,test_Y = test
        train_X = train_X.reshape(self.num_training_examples,28,28,1)
        test_X = test_X.reshape(test_X.shape[0],28,28,1)
        model = Sequential()
        
        model.add(Conv2D(32,kernel_size=(1,1),use_bias=False,input_shape=(28,28,1)))
        model.add(BatchNormalization(axis=3))
        model.add(Activation('relu'))
        model.add(Conv2D(64,kernel_size=(3,3),use_bias=False))
        model.add(BatchNormalization(axis=3))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        
        model.add(Conv2D(32,kernel_size=(1,1),use_bias=False))
        model.add(BatchNormalization(axis=3))
        model.add(Activation('relu'))
        model.add(Conv2D(64,kernel_size=(3,3),use_bias=False))
        model.add(BatchNormalization(axis=3))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Dropout(0.2))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))  
        model.add(Dropout(0.4))
        model.add(Dense(10, activation='softmax'))
    
        model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['categorical_accuracy','accuracy'])
        history = model.fit(train_X,train_Y, validation_split=0.2, epochs=self.number_of_epochs, batch_size=self.input['batch_size'])
        self.history = dict(history.history)
        self.param = self.input
        self.next(self.train_convolution_batch_norm_join)

    @step
    def train_convolution_batch_norm_join(self,inputs):
        """
        Result Data from parallel training sessions run over different hyper params for Conv Batch norm NN is collated in this step
        """
        self.history = [{'param':input_val.param,'history':input_val.history} for input_val in inputs]
        self.next(self.join)
    
    @step
    def train_convolution_join(self,inputs):
        """
        Result Data from parallel training sessions run over different hyper params for Conv NN is collated in this step
        """
        self.history = [{'param':input_val.param,'history':input_val.history} for input_val in inputs]
        self.next(self.join)
    
    @step
    def train_sequential_join(self,inputs):
        """
        Result Data from parallel training sessions run over different hyper params for Sequential NN is collated in this step
        """
        self.history = [{'param':input_val.param,'history':input_val.history} for input_val in inputs]
        self.next(self.join)
    
    @step
    def join(self,inputs):
        """
        All the Traininig results are collated into a single object in the step of the flow. 
        """
        self.history = {
            'convolution' : inputs.train_convolution_join.history,
            'sequential' : inputs.train_sequential_join.history,
            'convolution_batch_norm' : inputs.train_convolution_batch_norm_join.history
        }
        
        self.next(self.end)

    @step
    def end(self):
        """
        This is the end step of the Computation 
        """
        print("Done Computation")


if __name__ == '__main__':
    MultiStepMNISTFlow()