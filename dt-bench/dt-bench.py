#!/usr/bin/python
import os
import xlsxwriter
import random
import time
import argparse
# multimachine benchmarks configure
#-------------------------------------------------------------------------
if __name__ == "__main__":

    sync_methods = None
    dnn_models = None
    gpu_number = 1
    all_reduce_spec = 'nccl/xring'
    # if server_protocol='grpc+verbs', RDMA_DEVICE must be specified(e.g.
    # RDMA_DEVICE=mlx5_3).
    server_protocol = 'grpc'
    data_dir = ''

    parser = argparse.ArgumentParser(description='DT-Bench')
    parser.add_argument(
        '--variable_updates', metavar='<LIST_OF_VARIABLE_UPDATES>', type=str, required=True,
            help='string of variable_update methods, e.g. "parameter_server,replicated,distributed_replicated"')
    parser.add_argument(
        '--models', metavar='<LIST_OF_MODELS>', type=str, required=True,
            help='string of variable_update methods, e.g. "alexnet,resnet50"')
    parser.add_argument(
        '--num_gpus', type=int, required=False, metavar='n_GPUs',
            help='number of GPUs')
    parser.add_argument(
        '--all_reduce_spec', type=str, required=False, metavar='SPEC',
            help='all_reduce approach: e.g. nccl, xring')
    parser.add_argument(
        '--server_protocol', type=str, required=False, metavar='SPEC',
            help='server protocol to exchange parameters: e.g. grpc, grpc+verbs, grpc+gdr')
    parser.add_argument('--data_dir', type=str, required=False, metavar='DIR',
                        help='path to directory of dataset')
    args = parser.parse_args()

    variable_update = args.variable_updates.split(',')
    models = args.models.split(',')
    if args.num_gpus is not None:
        gpu_number = args.num_gpus
    if args.all_reduce_spec is not None:
        all_reduce_spec = args.all_reduce_spec
    if args.server_protocol is not None:
        server_protocol = args.server_protocol
    if args.data_dir is not None:
        data_dir = args.data_dir
    print(variable_update)
    print(models)
    num_batches = 100

    min_batch_size = 32
    max_batch_size = 64
    gpu_memory_frac_for_testing = 0.45
    ps = ['node0']
    worker = ['node0']

    # Device to use  as parameter server: cpu or gpu
    local_parameter_device = 'cpu'
    # end of address do not include '/'
    remote_log_file_address = '~/dt-bench-log-r'
    local_log_address = '~/dt-bench-log-l'
    file_address = '~/scout/t-bench/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py'

    # if you don't need to use virtualenv, modify to ''
    # virtualenv example = '/home/hong/virtialenv_dir/bin/'
    virtualenv = 'source ~/setenv.sh ; source ~/tf-v1.5.0-rc1-none/bin/activate ; source ~/apps/sofa/tools/activate.sh ; '
    # virtualenv = 'source ~/setenv.sh ;  '

    profile_begin = ''
    profile_end = ''
    #profile_begin = 'sofa record \"'
    #profile_end = '\"'
    ps_profile_begin = ''
    ps_profile_end = ''
    # ps_profile_begin = 'source ~/apps/sofa/tools/activate && sofa record \"'
    # ps_profile_end = '\"'

    # -----------------------------------------------------------------------------------

    # for batch size 1, 2, 4, 8, .....
    def doubling_range(start, stop):
        while start < stop:
            yield start
            start <<= 1

    # result_array prepare for the excel
    batch_num_array = []
    for i in doubling_range(min_batch_size, (max_batch_size + 1)):
        batch_num_array.append(i)
    batch_num = len(batch_num_array) + 1

    # data = [[None] * batch_num for i in range(len(models) +1)]
    title = ['batch_size'] + models
    workbook = xlsxwriter.Workbook('dt-bench.xlsx')
    sheet1 = workbook.add_worksheet('parameter_server')
    sheet2 = workbook.add_worksheet('distributed_replicated')
    bold = workbook.add_format({'bold': 1})

    # xlsx model title and batch_size
    tmp = 0
    for a in title:
        sheet1.write(tmp, 0, a)
        sheet2.write(tmp, 0, a)
        tmp += 1
    tmp = 1
    for b in batch_num_array:
        sheet1.write(0, tmp, b)
        sheet2.write(0, tmp, b)
        tmp += 1

    # ps and worker port
    # 451952-58000 reserved for private, dynamic and temporary usages
    ps_rand = random.randrange(49152, 58000)
    worker_rand = random.randrange(58000, 65536)
    # ps_rand = 50000
    # worker_rand = 50001
    ps_p = [None] * len(ps)
    worker_p = [None] * len(worker)

    # cmd setting
    cmd_list = [None] * (len(ps) + len(worker))
    cmd_kill = [None] * len(ps)
    cmd_mkdir = [None] * len(worker)

    # create a script to kill program
    with open('kill.sh', 'w+') as fout:
        # fout.write('nvidia-smi | awk \'$5=="' + virtualenv  +  'python"
        # {print $3}\' | xargs kill -9\n')
        fout.write('nvidia-smi | awk \'$4=="C" {print $3}\' | xargs kill -9')
    kill_cmd = ' < kill.sh'

    # create remote log dir
    mkdir_cmd = 'mkdir -p ' + remote_log_file_address
    for c in range(len(worker)):
        cmd_mkdir[c] = 'ssh ' + worker[c] + ' \'' + mkdir_cmd + '\''
        os.system(cmd_mkdir[c])

    # trans log file to localhost
    download_remote_logs_cmd = 'scp -r ' + \
        worker[0] + ':' + remote_log_file_address + ' .'
    relocate_remote_logs_cmd = 'cp -rT ' + \
        os.path.basename(remote_log_file_address) + ' ' + local_log_address

    # split aaa@1.1.1.1 to 1.1.1.1:80 , and combine worker and ps cmd
    for i in range(len(ps)):
    #    ps_p[i] = ps[i].split('@')[1] + ':' + str(ps_rand)
        ps_p[i] = ps[i] + ':' + str(ps_rand)
    ps_cmd = ','.join(ps_p)

    for i in range(len(worker)):
    #    worker_p[i] = worker[i].split('@')[1] + ':' + str(worker_rand)
        worker_p[i] = worker[i] + ':' + str(worker_rand)
    worker_cmd = ','.join(worker_p)

    for variable in variable_update:
        for model in models:
            for i in doubling_range(min_batch_size, (max_batch_size + 1)):
                for a in range(len(ps)):
                    if a > 0:
                        ps_profile_begin = ''
                        ps_profile_end = ''
                    cmd_list[a] = 'ssh ' + ps[a] + ' \'' + virtualenv + ps_profile_begin + \
                                  'python ' + str(file_address) + \
                                  ' --model=' + str(model) + \
                                  ' --data_name=imagenet' + \
                                  ' --data_dir=' + data_dir + \
                                  ' --batch_size=' + str(i) + \
                                  ' --num_batches=' + str(num_batches) + \
                                  ' --num_gpus=' + str(gpu_number) + \
                                  ' --variable_update=' + str(variable) + \
                                  ' --job_name=ps' + \
                                  ' --controller_host=node0' + \
                                  ' --local_parameter_device=' + local_parameter_device + \
                                  ' --server_protocol=' + server_protocol + \
                                  ' --all_reduce_spec=' + all_reduce_spec + \
                                  ' --ps_hosts=' + ps_cmd  + \
                                  ' --worker_hosts=' + worker_cmd + \
                                  ' --gpu_memory_frac_for_testing=' + str(gpu_memory_frac_for_testing) + \
                                  ' --task_index=' + str(a) + \
                                  ' ' + ps_profile_end + \
                                  '\' &'
                for b in range(len(worker) - 1):
                    if b > 0:
                        profile_being = ''
                        profile_end = ''
                    cmd_list[len(ps) + b] = 'ssh ' + worker[b] + ' \'' + virtualenv + \
                        'python ' + str(file_address) + \
                        ' --model=' + str(model) + \
                        ' --data_name=imagenet' + \
                        ' --data_dir=' + data_dir + \
                        ' --batch_size=' + str(i) + \
                        ' --num_batches=' + str(num_batches) + \
                        ' --num_gpus=' + str(gpu_number) + \
                        ' --variable_update=' + str(variable) + \
                        ' --job_name=worker' + \
                        ' --controller_host=node0' + \
                        ' --local_parameter_device=' + local_parameter_device + \
                        ' --server_protocol=' + server_protocol + \
                        ' --all_reduce_spec=' + all_reduce_spec + \
                        ' --ps_hosts=' + ps_cmd + \
                        ' --worker_hosts=' + worker_cmd  + \
                        ' --gpu_memory_frac_for_testing=' + str(gpu_memory_frac_for_testing) + \
                        ' --task_index=' + str(b)  + \
                        ' > ' + remote_log_file_address + '/' + str(model) + '_' + str(i) + '_' + str(variable) + '.txt' + \
                        '\' &'

                cmd_list[len(ps) + len(worker) - 1] = 'ssh ' + worker[-1] + ' \'' + virtualenv + ' timeout 120 ' +  \
                    profile_begin + \
                    ' python ' + str(file_address) + \
                    ' --model=' + str(model) + \
                    ' --data_name=imagenet' + \
                    ' --data_dir=' + data_dir + \
                    ' --batch_size=' + str(i) + \
                    ' --num_batches=' + str(num_batches) + \
                    ' --num_gpus=' + str(gpu_number) + \
                    ' --variable_update=' + str(variable) + \
                    ' --job_name=worker' + \
                    ' --controller_host=node0' + \
                    ' --local_parameter_device=' + local_parameter_device + \
                    ' --server_protocol=' + server_protocol + \
                    ' --all_reduce_spec=' + all_reduce_spec + \
                    ' --ps_hosts=' + ps_cmd + \
                    ' --worker_hosts=' + worker_cmd  + \
                    ' --task_index=' + str(len(worker) - 1)  + \
                    ' --gpu_memory_frac_for_testing=' + str(gpu_memory_frac_for_testing) + \
                    ' > ' + remote_log_file_address + '/' + str(model) + '_' + str(i) + '_' + str(variable) + '.txt' + \
                    ' ' + profile_end + \
                    '\' '

                # for to execute command
                for cmd in cmd_list:
                    print cmd
                    os.system(cmd)

                time.sleep(20)

                # kill ps process
                for a in range(len(ps)):
                    cmd_kill[a] = 'ssh ' + ps[a] + kill_cmd
                for kill in cmd_kill:
                    print kill
                    os.system(kill)

                time.sleep(20)
                # receive log file

    print download_remote_logs_cmd
    os.system(download_remote_logs_cmd)
    os.remove('./kill.sh')

    print relocate_remote_logs_cmd
    os.system(relocate_remote_logs_cmd)

    for variable in variable_update:
        for model in models:
            for i in doubling_range(min_batch_size, (max_batch_size + 1)):
                log_path = local_log_address + '/' + \
                    str(model) + '_' + str(i) + '_' + str(variable) + '.txt'
                print log_path
                if os.path.exists(log_path):
                    with open(log_path) as f:
                        if os.path.getsize(log_path) > 0:
                            txt = f.readlines()

                            if txt[-1] != '----------------------------------------------------------------\n':
                                result_number = '0\n'
                                print variable, model, i, 'img/sec : ', result_number

                            else:
                                keys = [r for r in range(1, len(txt) + 1)]

                                # result is dictionary that each key represent
                                # each line in output.txt
                                result = {
                                    k: v for k, v in zip(keys, txt[::-1])}

                                # cut result to ['total images/sec', 'xx.xx']
                                result[2].split(': ')

                                result_number = result[2].split(': ')[1]
                                print variable, model, i, 'img/sec : ', result_number
                        else:
                            result_number = '0\n'
                else:
                    result_number = '0\n'

    # write the result back to excel file
                if variable == 'parameter_server':
                    sheet1.write(
                        models.index(model) + 1,
                        batch_num_array.index(i) + 1,
                        round(float(result_number)))
                elif variable == 'distributed_replicated':
                    sheet2.write(
                        models.index(model) + 1,
                        batch_num_array.index(i) + 1,
                        round(float(result_number)))
                elif variable == 'distributed_all_reduce':
                    sheet2.write(
                        models.index(model) + 1,
                        batch_num_array.index(i) + 1,
                        round(float(result_number)))

    #
    #
    # Create a new column chart.#
    chart1 = workbook.add_chart({'type': 'column'})
    chart2 = workbook.add_chart({'type': 'column'})

    # Configure series. Note use of alternative syntax to define ranges.
    for k in batch_num_array:
        chart1.add_series({
            'name':
                ['parameter_server', 0, batch_num_array.index(k) + 1],
            'categories': ['parameter_server', 1, 0, len(models), 0],
            'values':
                ['parameter_server', 1, batch_num_array.index(
                    k) + 1, len(models), batch_num_array.index(k) + 1],
            'data_labels': {'value': True},
        })
        chart2.add_series({
            'name':
                ['distributed_replicated', 0, batch_num_array.index(k) + 1],
            'categories': ['distributed_replicated', 1, 0, len(models), 0],
            'values':
                ['distributed_replicated',
                         1,
                         batch_num_array.index(
                 k) + 1,
                         len(models),
                    batch_num_array.index(k) + 1],
            'data_labels': {'value': True},
        })

    # Add a chart title and some axis labels.
    chart1.set_title({'name': 'Variable Update Parameter_server'})
    chart1.set_x_axis({'name': 'models'})
    chart1.set_y_axis({'name': 'img/sec'})

    chart2.set_title({'name': 'Variable Update Distributed_Replicated'})
    chart2.set_x_axis({'name': 'models'})
    chart2.set_y_axis({'name': 'img/sec'})

    # Set an Excel chart style.
    chart1.set_style(11)
    chart2.set_style(11)

    # Insert the chart into the worksheet (with an offset).
    sheet1.insert_chart(
        'A' + str(len(models) + 5),
        chart1,
     {'x_offset': 25,
      'y_offset': 10})
    sheet2.insert_chart(
        'A' + str(len(models) + 5),
        chart2,
     {'x_offset': 25,
      'y_offset': 10})

    workbook.close()
