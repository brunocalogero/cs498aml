#! env python
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
#np.set_printoptions(threshold=np.nan)
folder_path = "./cifar-10-batches-py/"
num_pcas = 20
def unpickle(file):
    import cPickle
    fo = open(file, 'rb')
    dict = cPickle.load(fo)
    fo.close()
    return dict


def show_pic(data, name):
    pic = np.zeros((32,32,3))
    for i in range(32):
        for j in range(32):
            for k in range(3):
                pic[i,j,k] = data[1024*k + 32*j + i]/256.
    plt.imsave(fname=name, arr=pic)


meta_info = unpickle(folder_path + "batches.meta")
label_dict = meta_info["label_names"]
num_labels = len(label_dict)
num_dims = meta_info["num_vis"]
num_data = meta_info["num_cases_per_batch"]



batch = unpickle(folder_path + "data_batch_1")
data = np.array(batch["data"], dtype=np.float32)[0:1000]
labels = np.array(batch["labels"])[0:1000]
## Data preprocessing
split_data = [0]*num_labels
for label_i in range(num_labels):
    split_data[label_i] = data[labels == label_i]

error = [0]*num_labels
for label_i  in range(num_labels):
    print "working on " + label_dict[label_i]
    working_set = split_data[label_i]
    N= len(working_set)
    mean_image = np.zeros(num_dims)
    for data_i in range(N):
        mean_image += working_set[data_i]
    mean_image = mean_image/N
    show_pic(mean_image, "mean" + str(label_i))
    # centering the data
    for data_i in range(N):
        working_set[data_i] -= mean_image
    cov_mat = np.cov(working_set.T)
    eival, eivec = np.linalg.eig(cov_mat)
    for data_i in range(N):
        working_set[data_i] = np.dot(eivec.T, working_set[data_i])
    approx_data = np.zeros(working_set.shape)
    approx_data[:, 0:num_pcas] = working_set[:, 0:num_pcas]

    error_sum = 0.
    for data_i in range(N):
        error_sum += np.dot(approx_data[data_i], working_set[data_i])**2
    error[label_i] = (error_sum/N)

    # Todo make this plot nice looking
    plt.figure()
    plt.title("Principal components")
    plt.xlabel("$n^{th}$ greatest eigenvalue")
    plt.ylabel("Eigenvalue")
    plt.plot(eival)
    plt.savefig("PCA" + str(label_i))

plt.figure()
plt.title("Errors as a function of category")
categories = tuple(label_dict)
plt.bar(np.arange(len(categories)), error, align='center')
y_pos = np.arange(len(categories))
plt.xlabel("Label")
plt.xticks(y_pos, categories, rotation='vertical')
plt.ylabel("Error")
plt.savefig("errors")
