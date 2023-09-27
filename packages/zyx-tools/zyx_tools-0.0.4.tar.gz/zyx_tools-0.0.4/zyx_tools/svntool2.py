#! python3
#   . hproof, 2023/8/30, init
#   . svn 常用操作封装, 包括: 
#       . 查询: 
#           . get_status
#           . get_version
#           . get_last_commit
#       . 下载
#           . revert
#           . update
#           . revert_and_update
#       . 上传
#           . add_local_new_files
#           . commit_changed
#       . 所有操作 确保成功 
#           . 否则会抛异常 SvnError
#           . 可通过 error_handler 设置错误处理函数, 例如上报飞书群


import subprocess, os, re, tempfile
from cilib import mylog


# 全局变量
encoding = 'gb2312'         # 如果出现乱码, 可修改该值
error_handler = None        # 发生 svn 错误时, 调用的处理函数, 原型为 foo(msg:str)


# 提交信息
class CommitInfo:
    path : str
    revision : str
    author : str
    date : str
    message: str


# 深度信息
class Depth:
    empty = 'empty'
    files = 'files'
    immediates = 'immediates'
    infinity = 'infinity'


# 异常错误
class SvnError( Exception ):
    message : str
    def __init__( self, message ):
        self.message = message


# 抛出异常
def _raise_error( msg:str ):
    if error_handler:
        error_handler(msg)
    raise SvnError(msg)


# 运行 svn 命令, 检查错误, 并返回输出
def _run_command( args:list[str], check_error:bool=True ):
    proc = subprocess.Popen( args, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    outs, errs = proc.communicate()
    if check_error and errs:
        error = errs.decode( encoding )
        _raise_error(f'svn 命令执行失败! args:{args}, error:{error}')
    if outs:
        return outs.decode( encoding )
    return ''       # 部分 SVN 命令执行后 没有输出


# 获取 path 下的 externals
def _get_externals( path: str, result:list[str]=None ):
    if not result: result = []
    lines = _run_command( ['svn', 'propget', 'svn:externals', path, '-R'] ).splitlines()
    prefix = None
    for line in lines:
        if len(line) == 0: continue
        idx = line.find(' - ')
        if idx > 0:
            prefix = line[0:idx]
            line = line[idx + 3: ]
        idx = line.find(' ')
        if idx > 0:
            local = line[idx+1:]
            path2 = os.path.join( prefix, local )
            if not path2 in result:
                result.append( path2 )
                _get_externals( path2, result )     # 递归获取该 external 中的其它 externals
    return result


# 字典根据 key 获取 list
def _dict_get_or_add_list( d:dict, key ):
    value = d.get( key )
    if not value:
        value = []
        d[ key ] = value
    return value


# 获取状态, 返回: sub_path -> sub_dict; 其中 sub_dict = { flag -> [file]}
# flag 包括: L=锁定, A=添加, C=冲突, D=删除, M=修改, ?=不在版本库中, !=本地被删除
def get_status(path:str):
    lines = _run_command( ['svn', 'st', path] ).splitlines()
    sub_path = path
    sub_dict = {}
    status = {}
    for line in lines:
        if len(line) == 0: continue
        ch = line[0]
        if ch == 'P': 
            m = re.match(r"Performing status on external item at '(.*)'", line)
            if m: 
                if len(sub_dict) > 0:
                    status[ sub_path ] = sub_dict
                sub_path = m.group(1)
                sub_dict = {}
            continue
        if ch != ' ':
            _dict_get_or_add_list( sub_dict, ch ).append( line[8:] )
        ch = line[2]
        if ch != ' ':
            _dict_get_or_add_list( sub_dict, ch ).append( line[8:] )
    if len(sub_dict) > 0:
        status[ sub_path ] = sub_dict
    return status


# 获取 flags 集合
def get_status_flags( path_or_status ):
    status = path_or_status if isinstance( path_or_status, dict) else get_status( path_or_status )
    flags = [ flag for sub_dict in status.values() for flag in sub_dict.keys() ] 
    return set(flags)


# 获取文件列表
def get_status_files( path_or_status, flag:str ):
    status = path_or_status if isinstance( path_or_status, dict) else get_status( path_or_status )
    return [file for sub_dict in status.values() if flag in sub_dict for file in sub_dict[flag] ]


# 还原 path 及其子目录, 放弃本地所有修改
def revert(path:str, remove_local_news:bool=True):
    # 获取当前状态
    status = get_status( path )
    flags = get_status_flags( status )
    mylog.info('svn revert', path, 'flags', flags)
    # 根据状态执行还原
    changed = False
    if 'L' in flags:   # 锁定
        _run_command( ['svn', 'cleanup', path, '--include-externals' ] )
        changed = True
    # 循环处理每个 externals
    for sub_path, sub_dict in status.items():
        if 'A' in sub_dict or 'C' in sub_dict or 'D' in sub_dict or 'M' in sub_dict:    # 添加, 冲突, 删除, 修改
            _run_command( ['svn', 'revert', sub_path, '-q', '-R', '--remove-added' ])
            changed = True
        if '?' in sub_dict or 'A' in sub_dict: # 不在版本内的文件; 执行 revert 后 'A' 会变为 '?'
            if remove_local_news:
                _run_command( ['svn', 'cleanup', sub_path, '-q', '--remove-unversioned' ])
                changed = True
        if '!' in sub_dict: # 本地被删除, 可以通过 svn up 恢复
            pass        
    # 检查是否成功
    if changed:
        flags = get_status_flags( path )
        mylog.info('after revert status', flags)
        flags.discard('X')         # 忽略 外部连接
        flags.discard('!')         # 忽略 本地删除
        if not remove_local_news:   # 如果 不删除本地新文件, 忽略 本地新文件
            flags.discard('?')
        if len(flags) > 0:
            _raise_error(f'svn revert 失败! path:{path}, flags:{flags}')


# 更新目标; 如果当前不在版本库中 会报错
def update( path: str ):
    mylog.info('svn update', path)
    _run_command( ['svn', 'up', path, '-q', '--accept', 'theirs-full' ] )


# 更新目录
def revert_and_update( path: str ):
    revert(path)
    update(path)


# 返回版本号, 数字形式
def get_version( path : str ):
    output = _run_command( ['svn', 'info', path, '-r', 'BASE'] )
    m = re.search(r'Revision:\s(\d+)', output)
    if m: 
        return int( m.group(1) )


# 获取最后提交信息
def get_last_commit( path: str ):
    lines = _run_command( ['svn', 'log', path, '-l', '1'] ).splitlines()
    arr = lines[1].split(' | ')
    msg = ';'.join( lines[3:-1] )
    info = CommitInfo()
    info.path = path
    info.revision = arr[0]
    info.author = arr[1]
    info.date = arr[2]
    info.message = msg
    return info


# 添加本地新文件, 返回文件列表; 标记 '?' 会变为 'A'
def add_local_new_files( path: str ):
    files = get_status_files( path, '?' )
    if len(files) > 0:
        mylog.info('svn add', files)
        for x in files:
            args = ['svn', 'add', x, '-q']
            _run_command( args  )
        return files


# 写入到临时文件
def _write_temp_file_lines( lines:list ):
    f = tempfile.NamedTemporaryFile('w', encoding=encoding)
    for line in lines:
        f.write( line )
        f.write('\n')
    f.flush()
    return f


# 提交修改, 包括 'A', 'M'
def commit_changed( path:str, msg:str ):
    status = get_status( path )
    flags = get_status_flags( status )
    # 检查错误
    if 'L' in flags:
        _raise_error(f'svn 已经被锁定! path:{path}, flags:{flags}')
    if 'C' in flags:
        _raise_error(f'存在 svn 冲突! path:{path}, flags:{flags}')
    # 执行提交
    files = []
    for flag in ['A', 'M']:
        files.extend( get_status_files( status, flag ) )
    if len(files) > 0:
        mylog.info('svn commit', path, msg, files)
        f = _write_temp_file_lines( files )
        _run_command( ['svn', 'ci', '-m', msg, '-q', '--targets', f.name] )