import os
import xlsxwriter
import shutil

# single machine benchmarks configure
#-----------------------------------------------------------------------------------

models = ['resnet50', 'resnet152', 'inception3', 'alexnet', 'vgg16']
gpu_number = 2
local_parameter_device = 'gpu'
file_address = '/home/paslab/yihong/benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py'
log_address = '/home/paslab/yihong/dt-bench/log_single'
variable_update = ['parameter_server', 'replicated']
max_batch_size = 64

# if you don't need to use virtualenv, modify to virtualenv = ''
virtualenv = '/home/paslab/yihong/tensorflow_vir1.4/bin/'

# -----------------------------------------------------------------------------------

def doubling_range(start, stop):
    while start < stop:
        yield start
        start <<=1

# result_array prepare for the excel
batch_num_array = []
for i in doubling_range(1, (max_batch_size + 1)):
	batch_num_array.append(i)
batch_num = len(batch_num_array) + 1
# data = [[None] * batch_num for i in range(len(models) +1)]
title = ['batch_size'] + models
workbook = xlsxwriter.Workbook('t-bench.xlsx')
sheet1 = workbook.add_worksheet('parameter_server')
sheet2 = workbook.add_worksheet('replicated')  
bold = workbook.add_format({'bold': 1})

# create log dir 
if not os.path.exists(log_address):
        os.makedirs(os.path.basename(log_address))

tmp = 0			
for a in title :
	sheet1.write(tmp, 0, a)
	sheet2.write(tmp, 0, a)
	tmp += 1
tmp = 1
for b in batch_num_array :
	sheet1.write(0, tmp, b)
	sheet2.write(0, tmp, b)
	tmp += 1

for variable in variable_update:
	for model in models:
    
    		# adjust batch_size here ,default is 1 to 64
    		for i in doubling_range(1, (max_batch_size + 1)):

			bench = str(virtualenv) + 'python ' + str(file_address) + \
                                ' --model='+ str(model) + \
                                ' --batch_size=' + str(i) + \
                                ' --num_gpus=' + str(gpu_number) + \
                                ' --variable_update=' + str(variable) + \
				' --local_parameter_device=' + local_parameter_device + \
                                ' > '  + str(model) + '_' + str(i) + '_' + str(variable) + '.txt'
			os.system(bench)
                        print bench, '\n'
                        #shutil.move(os.getcwd() + '/' + str(model) + '_' + str(i) + '_' + str(variable) + '.txt', os.path.basename(log_address))
			mv_cmd = 'mv *.txt' + ' ' + os.path.basename(log_address)
			os.system(mv_cmd)
                        log_path = log_address + '/' + str(model) + '_' + str(i) + '_' + str(variable) + '.txt'
                        print log_path
                        if os.path.exists(log_path):
			    with open(log_path) as f:
                                if os.path.getsize(log_path) > 0:
                                    txt = f.readlines()
			       
                                    if txt[-1] or txt[-3] != '----------------------------------------------------------------\n' :
                                        result_number = int(0)
                                        print variable, model, i, 'img/sec : ' ,result_number
                                
                                    else:
                                        keys=[r for r in range(1,len(txt)+1)]

			                # result is dictionary that each key represent each line in output.txt
			                result = {k:v for k,v in zip(keys,txt[::-1])}

			                # cut result to ['total images/sec', 'xx.xx']
		        	        result[2].split(': ') 

			                result_number = result[2].split(': ')[1] 
                                        print variable, model, i, 'img/sec : ' ,result_number
                                else:
                                    result_number = '0\n'
                        else:
                            result_number = '0\n'

# write the result back to excel file
			if variable == 'parameter_server' :
				sheet1.write(models.index(model)+1, batch_num_array.index(i)+1, round(float(result_number)))
			elif variable == 'replicated' :
				sheet2.write(models.index(model)+1, batch_num_array.index(i)+1, round(float(result_number)))
 
#######################################################################
#
# Create a new column chart.
#
chart1 = workbook.add_chart({'type': 'column'})
chart2 = workbook.add_chart({'type': 'column'})

# Configure series. Note use of alternative syntax to define ranges.
for k in batch_num_array :
    chart1.add_series({
        'name':       ['parameter_server', 0, batch_num_array.index(k)+1],
        'categories': ['parameter_server', 1, 0, len(models), 0],
        'values':     ['parameter_server', 1, batch_num_array.index(k)+1 , len(models) , batch_num_array.index(k)+1 ],
        'data_labels': {'value': True},
                })
    chart2.add_series({
        'name':       ['replicated', 0, batch_num_array.index(k)+1],
        'categories': ['replicated', 1, 0, len(models), 0], 
        'values':     ['replicated', 1, batch_num_array.index(k)+1 , len(models) , batch_num_array.index(k)+1 ],                                                              
        'data_labels': {'value': True},
                })
 
# Add a chart title and some axis labels.
chart1.set_title ({'name': 'Variable Update Parameter_server'})
chart1.set_x_axis({'name': 'models'})
chart1.set_y_axis({'name': 'img/sec'})
 
chart2.set_title ({'name': 'Variable Update Replicated'})
chart2.set_x_axis({'name': 'models'})
chart2.set_y_axis({'name': 'img/sec'})

# Set an Excel chart style.
chart1.set_style(11)
chart2.set_style(11) 

# Insert the chart into the worksheet (with an offset).
sheet1.insert_chart('A'+str(len(models) +5), chart1, {'x_offset': 25, 'y_offset': 10})
sheet2.insert_chart('A'+str(len(models) +5), chart2, {'x_offset': 25, 'y_offset': 10})

workbook.close()
