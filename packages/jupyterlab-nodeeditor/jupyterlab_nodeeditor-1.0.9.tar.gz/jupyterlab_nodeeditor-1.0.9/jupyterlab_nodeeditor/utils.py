import json
import io
import os
import base64
import inspect
from svg.path import parse_path
from svg.path.path import segment_length, MIN_DEPTH, ERROR


def get_instance_info(v):
    from .select import select, mselect
    t = type(v)
    d = None
    if isinstance(v, int) \
            or isinstance(v, float) \
            or isinstance(v, str) \
            or isinstance(v, bool):
        d = v
    if isinstance(v, select) \
            or isinstance(v, mselect):
        d = v.get_show_options()

    return json.dumps({"type": str(t), "value": d})

def get_urls_list(urls):
    # 如果urls是字符串
    if isinstance(urls, str):
        try:
            ret = json.loads(urls)
            if not isinstance(ret, list):
                raise TypeError('Expecting a list')
            return ret
        except ValueError as e:
            if urls.startswith('http') or urls.startswith('data:image'):
                return [urls]
            elif os.path.exists(urls) and os.path.isfile(urls):
                with open(urls, 'rb') as fp:
                    data = fp.read()
                    data = base64.b64encode(data).decode()
                url = 'data:image/png;base64,' + data
                return [url]
        except TypeError as e:
            raise TypeError('Invalid input type')
    
    # 如果urls是列表
    if isinstance(urls, list):
        ret = []
        for url in urls:
            try:
                ret_urls = get_urls_list(url)
                for ret_url in ret_urls:
                    ret.append(ret_url)
            except:
                pass
        return ret
    
    # 如果urls是字典
    if isinstance(urls, dict):
        return list(urls.values())
    
    # 如果urls是cv2的numpy.ndarry
    try:
        import cv2
        from numpy import ndarray
        if isinstance(urls, ndarray):
            img = cv2.cvtColor(urls, cv2.COLOR_RGB2BGR)
            img_bytes = cv2.imencode('.png', img)[1].tobytes()
            img_b64 = base64.b64encode(img_bytes).decode()
            img_url = "data:image/png;base64," + img_b64
            return [img_url]
    except:
        pass
    
    # 如果urls是matplotlib的画布
    try:
        from matplotlib.figure import Figure
        from matplotlib.image import AxesImage
        import matplotlib.pyplot as plt
        if urls == plt:
            fig = urls
        if isinstance(urls, Figure):
            fig = urls
        if isinstance(urls, AxesImage) :
            fig = urls.get_figure()
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches=None)
        url = 'data:image/png;base64,' + \
            base64.b64encode(buffer.getvalue()).decode()
        return [url]
    except:
        pass

    # 如果urls是PILLOW的Image
    try:
        from PIL import Image
        if isinstance(urls, Image):
            buffer = io.BytesIO()
            urls.save(buffer, format="PNG")
            url = 'data:image/png;base64,' + \
                base64.b64encode(buffer.getvalue()).decode()
            return [url]
    except:
        pass
    raise TypeError('Invalid input type')

def get_urls(urls):
    ret = get_urls_list(urls)
    return json.dumps(ret)

def get_boolean_value(v):
    if v:
        return True
    else:
        return False

def get_svg_path_y_value(svg_path, x_value):
    path = parse_path(svg_path)
    for segment in path:
        if hasattr(segment, 'start') and hasattr(segment, 'end'):
            if segment.start.real <= x_value <= segment.end.real:
                qujian = segment.end.real - segment.start.real
                if qujian == 0:
                    t = 0
                else:
                    t = (x_value - segment.start.real) / qujian
                return segment.point(t).imag
    return None

def get_svg_path_length(svg_path, end_x):
    path = parse_path(svg_path)
    ret = 0
    for segment in path:
        if hasattr(segment, 'start') \
        and hasattr(segment, 'end') \
        and segment.start.real <= end_x <= segment.end.real:
            qujian = segment.end.real - segment.start.real
            t = qujian == 0 and 0 or (end_x - segment.start.real) / qujian
            ret += segment_length(segment, 
                                0, 
                                t, 
                                segment.point(0), 
                                segment.point(t), 
                                ERROR, 
                                MIN_DEPTH, 
                                0)
            return ret
        else:
            ret += segment.length()
    return None

def get_function_arg_select_value(fn, param_name, index):
    sig = inspect.signature(fn)
    s = sig.parameters[param_name].annotation
    return s.get_option_value(index)

# def importNodeTypesFromNotebook(path):
#     ret = {}
#     with open(path) as fp:
#         data = json.load(fp)
#     for cell in data['cells']:
#         code = ""
#         for line in cell['source']:
#             code += line + "\n"
#         code = code[:-1]
#         m: re.Match = re.search("#\[nodes_(.*?)\]\[\S*?\](.*)", code)
#         if m is not None:
#             nodesData = json.loads(m.group(2))
#             nodeTypes = nodesData.get("nodeTypes")
#             if nodeTypes is not None:
#                 ret.update(nodeTypes)
#     return ret


# loadCache = {}


# def importNotebook(path):
#     if not os.path.exists(path):
#         return
#     ret = loadCache.get(path)
#     if ret:
#         return ret
#     cache = import_ipynb.find_notebook
#     import_ipynb.find_notebook = lambda fullname, path: fullname
#     loader = import_ipynb.NotebookLoader()
#     try:
#         ret = loader.load_module(path)
#         loadCache[path] = ret
#     except ... as e:
#         raise e
#     finally:
#         import_ipynb.find_notebook = cache
#     return ret


# def loadNotebook(path):
#     importNotebook(path)
#     nodeTypes = importNodeTypesFromNotebook(path)


if __name__ == "__main__":
    d = "M 0 300  C 69.46334838867188 -179.05067097924663 138.92669677734375 267.10610712652294 208.39004516601562 170.26177978515625 Q  277.8533935546875 73.41745244378956 300 0"  
    x = 120
    print(get_svg_y_value(d, x)) 
    print(get_svg_length(d, 100))
    print(get_svg_length(d, 300))
