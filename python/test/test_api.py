import os
import shutil
import numpy as np

import trexio as tr

#=========================================================#
#======== SETUP THE BACK END AND OUTPUT FILE NAME ========#
#=========================================================#

# 0: TREXIO_HDF5 ; 1: TREXIO_TEXT
TEST_TREXIO_BACKEND = tr.TREXIO_TEXT
OUTPUT_FILENAME_TEXT = 'test_py_swig.dir'
OUTPUT_FILENAME_HDF5 = 'test_py_swig.h5'


# define TREXIO file name
if TEST_TREXIO_BACKEND == tr.TREXIO_HDF5:
    output_filename = OUTPUT_FILENAME_HDF5
elif TEST_TREXIO_BACKEND == tr.TREXIO_TEXT:
    output_filename = OUTPUT_FILENAME_TEXT
else:
    raise ValueError ('Specify one of the supported back ends as TEST_TREXIO_BACKEND')


# remove TREXIO file if exists in the current directory
try:
    if TEST_TREXIO_BACKEND == tr.TREXIO_HDF5:
        os.remove(output_filename)
    elif TEST_TREXIO_BACKEND == tr.TREXIO_TEXT:
        shutil.rmtree(output_filename)
except:
    print ('Nothing to remove.')

#=========================================================#
#============ WRITE THE DATA IN THE TEST FILE ============#
#=========================================================#

# create TREXIO file and open it for writing
#test_file = tr.open(output_filename, 'w', TEST_TREXIO_BACKEND)
test_file = tr.File(output_filename, mode='w', back_end=TEST_TREXIO_BACKEND)

# Print docstring of the tr.open function
#print(tr.open.__doc__)

nucleus_num = 12

# write nucleus_num in the file
tr.write_nucleus_num(test_file, nucleus_num)

# initialize charge arrays as a list and convert it to numpy array
charges = [6., 6., 6., 6., 6., 6., 1., 1., 1., 1., 1., 1.]
#charges_np = np.array(charges, dtype=np.float32)
charges_np = np.array(charges, dtype=np.int32)

# function call below works with both lists and numpy arrays, dimension needed for memory-safety is derived 
# from the size of the list/array by SWIG using typemaps from numpy.i
tr.write_nucleus_charge(test_file, charges_np)

# initialize arrays of nuclear indices as a list and convert it to numpy array
indices = [i for i in range(nucleus_num)]
# type cast is important here because by default numpy transforms a list of integers into int64 array
indices_np = np.array(indices, dtype=np.int64)

# function call below works with both lists and numpy arrays, dimension needed for memory-safety is derived 
# from the size of the list/array by SWIG using typemacs from numpy.i
tr.write_basis_nucleus_index(test_file, indices_np)

# initialize a list of nuclear coordinates
coords = [
  0.00000000 ,  1.39250319 ,  0.00000000 ,
 -1.20594314 ,  0.69625160 ,  0.00000000 ,
 -1.20594314 , -0.69625160 ,  0.00000000 ,
  0.00000000 , -1.39250319 ,  0.00000000 ,
  1.20594314 , -0.69625160 ,  0.00000000 ,
  1.20594314 ,  0.69625160 ,  0.00000000 ,
 -2.14171677 ,  1.23652075 ,  0.00000000 ,
 -2.14171677 , -1.23652075 ,  0.00000000 ,
  0.00000000 , -2.47304151 ,  0.00000000 ,
  2.14171677 , -1.23652075 ,  0.00000000 ,
  2.14171677 ,  1.23652075 ,  0.00000000 ,
  0.00000000 ,  2.47304151 ,  0.00000000 ,
  ]

# write coordinates in the file
tr.write_nucleus_coord(test_file, coords)

point_group = 'B3U'

# write nucleus_point_group in the file
tr.write_nucleus_point_group(test_file, point_group)

labels = [
        'C',
        'C',
        'C',
        'C',
        'C',
        'C',
        'H',
        'H',
        'H',
        'H',
        'H',
        'H']

# write nucleus_label in the file
tr.write_nucleus_label(test_file,labels)

# close TREXIO file 
# [TODO:] this functional call is no longer needed as we introduced TREXIO_File class which has a desctructor that closes the file
#tr.close(test_file)
# [TODO:] without calling destructor on test_file the TREXIO_FILE is not getting created and the data is not written when using TEXT back end. This, the user still has to explicitly call destructor on test_file object instead 
# tr.close function. This is only an issue when the data is getting written and read in the same session (e.g. in Jupyter notebook)
del test_file

#==========================================================#
#============ READ THE DATA FROM THE TEST FILE ============#
#==========================================================#

# open previously created TREXIO file, now in 'read' mode
#test_file2 = tr.open(output_filename, 'r', TEST_TREXIO_BACKEND)
test_file2 = tr.File(output_filename, 'r', TEST_TREXIO_BACKEND)

# read nucleus_num from file
rnum = tr.read_nucleus_num(test_file2)
assert rnum==nucleus_num

# safe call to read_nucleus_charge array of float values
rcharges_np = tr.read_nucleus_charge(test_file2, dim=nucleus_num)
assert rcharges_np.dtype is np.dtype(np.float64)
np.testing.assert_array_almost_equal(rcharges_np, charges_np, decimal=8)

# unsafe call to read_safe should fail with error message corresponding to TREXIO_UNSAFE_ARRAY_DIM
try:
    rcharges_fail = tr.read_nucleus_charge(test_file2, dim=nucleus_num*5)
except Exception:
    print("Unsafe call to safe API: checked")

# safe call to read array of int values (nuclear indices)
rindices_np_16 = tr.read_basis_nucleus_index(test_file2, dim=nucleus_num, dtype=np.int16)
assert rindices_np_16.dtype is np.dtype(np.int16)
for i in range(nucleus_num):
    assert rindices_np_16[i]==indices_np[i]

rindices_np_32 = tr.read_basis_nucleus_index(test_file2, dim=nucleus_num, dtype=np.int32)
assert rindices_np_32.dtype is np.dtype(np.int32)
for i in range(nucleus_num):
    assert rindices_np_32[i]==indices_np[i]

rindices_np_64 = tr.read_basis_nucleus_index(test_file2)
assert rindices_np_64.dtype is np.dtype(np.int64)
assert rindices_np_64.size==nucleus_num
for i in range(nucleus_num):
    assert rindices_np_64[i]==indices_np[i]

# read nuclear coordinates without providing optional argument dim
rcoords_np = tr.read_nucleus_coord(test_file2)
assert rcoords_np.size==nucleus_num*3

# read array of nuclear labels
rlabels_2d = tr.read_nucleus_label(test_file2, dim=nucleus_num)
print(rlabels_2d)
for i in range(nucleus_num):
    assert rlabels_2d[i]==labels[i]

# read a string corresponding to nuclear point group
rpoint_group = tr.read_nucleus_point_group(test_file2)
assert rpoint_group==point_group 

# close TREXIO file
#tr.close(test_file2)

# cleaning (remove the TREXIO file)
try:
    if TEST_TREXIO_BACKEND == tr.TREXIO_HDF5:
        os.remove(output_filename)
    elif TEST_TREXIO_BACKEND == tr.TREXIO_TEXT:
        shutil.rmtree(output_filename)
except:
    print (f'No output file {output_filename} has been produced')

#==========================================================#

