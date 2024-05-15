path = "SLIM_SandTank_test_cgrid.00000010.vtk"
import vtk
reader = vtk.vtkStructuredGridReader()
reader.SetFileName(path)
reader.Update()
imageData = reader.GetOutput()
array = imageData.GetCellData().GetArray('Concentration')
dataRange = array.GetRange(0)
print(dataRange)
