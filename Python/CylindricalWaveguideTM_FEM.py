import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import scipy.sparse as sp

a = 1

# Create Geometry
R = np.linspace(0, a, 50)
Theta = np.linspace(0, 2*np.pi, 100)

R_matrix, Theta_matrix = np.meshgrid(R, Theta)
X_n = R_matrix * np.cos(Theta_matrix)
Y_n = R_matrix * np.sin(Theta_matrix)
X = X_n.reshape(X_n.size)
Y = Y_n.reshape(Y_n.size)

triang = mtri.Triangulation(X, Y)
tri_coords = np.zeros((triang.triangles.shape[0], 3, 2))
for i, tri in enumerate(triang.triangles):
    tri_coords[i] = np.column_stack((X[tri], Y[tri]))


nodes = np.column_stack((triang.x, triang.y))
unique_nodes = np.unique(nodes, axis=0)
element_nodes = triang.triangles
Nn = nodes.shape[0]

# Define known and unknown fields
node_id = np.ones(nodes.shape[0])
Ez = np.zeros(nodes.shape[0])
for inode in range(0, nodes.shape[0]):
    radius = np.sqrt(pow(nodes[inode][0],2) + pow(nodes[inode][1], 2))
    if abs(radius-a) <= pow(10,-6):
        node_id[inode] = 0
        Ez[inode] = 0


# Index of unkowns
un_index = np.zeros(nodes.size, dtype=int)
counter = 0
for inode in range(0, nodes.shape[0]):
    if node_id[inode] == 1:
        un_index[inode] = counter
        counter = counter + 1


# Matrix Calculation
Nf = counter
S = sp.lil_matrix((Nf, Nf), dtype = float)
T = sp.lil_matrix((Nf, Nf), dtype = float)


for ie in range(1, triang.triangles.shape[0]):
    t_c = tri_coords[ie]
    x = np.zeros(3)
    y = np.zeros(3)
    x = [t_c[0][0], t_c[1][0], t_c[2][0]]
    y = [t_c[0][1], t_c[1][1], t_c[2][1]]
    n = [element_nodes[ie][0], element_nodes[ie][1], element_nodes[ie][2]]
        
    A = np.array([[1, x[0], y[0]], [1, x[1], y[1]], [1, x[2], y[2]]])
    De = np.linalg.det(A)
    Ae = abs(De/2)
    b = np.zeros(3)
    c = np.zeros(3)
    b = [(y[1]-y[2])/De, (y[2]-y[0])/De, (y[0]-y[1])/De]
    c = [(x[2]-x[1])/De, (x[0]-x[2])/De, (x[1]-x[0])/De]

    Se = np.zeros([3, 3])
    Te = np.zeros([3, 3])
    for i in range(0, 3):
        for j in range(0, 3):
            Se[i][j] = (b[i]*b[j] + c[i]*c[j])*Ae
            if i == j:
                Te[i][j] = Ae/6
            else:
                Te[i][j] = Ae/12

            if node_id[n[i]] == 1:
                if node_id[n[j]] == 1:
                    S[un_index[n[i]], un_index[n[j]]] = S[un_index[n[i]], un_index[n[j]]] + Se[i][j]
                    T[un_index[n[i]], un_index[n[j]]] = T[un_index[n[i]], un_index[n[j]]] + Te[i][j]



# Field and cut-off frequency calculation
k = 6
sigma = 0.1
M = sp.eye(Nf)
vals, vecs = sp.linalg.eigs(S - sigma*T, k, M=M, which='SM')

vecs = np.real(vecs)
vals = np.real(vals)

# Plot the results
fig, axs = plt.subplots(2, 3, figsize=(20, 10))
for i in range(0,2):
    for j in range(0,3):
        
        for inode in range(0, Nn):
            if node_id[inode] == 1:
                Ez[inode] = vecs[un_index[inode], i+j+1]

        axs[i][j].triplot(triang)
        cax = axs[i][j].tripcolor(triang, Ez, cmap='plasma', shading='flat')
        fig.colorbar(cax, ax=axs[i][j])

plt.show()