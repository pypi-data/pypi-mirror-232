import { FlumeConfig, Colors, Controls, SvgContainerStyle } from '../flume'
import React, { useState, useCallback, useRef, useEffect } from 'react'
import { NodeEditorWidget } from './widget'
import { buildNodeWidth } from './utils'
import * as monaco from 'monaco-editor';
import { Notification } from '@jupyterlab/apputils'
import CurveEditor from './CurveEditor';

export let headerFontsize = 16
export let nodeMinWidth = 200
export let nodeMaxWidth = 1000

let image_urls_functions: any = {}
export function setImageUrls(node_id, urls) {
    let setUrls = image_urls_functions[node_id]
    if (setUrls) {
        setUrls(urls)
    }
}

export function refreshImageUrls(widget: NodeEditorWidget) {
    let remove_list: any[] = []
    for (const nodeId in image_urls_functions) {
        if (!widget.editorNodes[nodeId]) {
            remove_list.push(nodeId)
        }
    }
    for (const nodeId of remove_list) {
        delete image_urls_functions[nodeId]
    }
}


let text_viewer_text_functions: any = {}
export function setTextViewerText(node_id, text) {
    let setText = text_viewer_text_functions[node_id]
    if (setText) {
        setText(text)
    }
}

export function refreshTextViewerText(widget: NodeEditorWidget) {
    let remove_list: any[] = []
    for (const nodeId in text_viewer_text_functions) {
        if (!widget.editorNodes[nodeId]) {
            remove_list.push(nodeId)
        }
    }
    for (const nodeId of remove_list) {
        delete text_viewer_text_functions[nodeId]
    }
}


let tupleCache = {}
let dictCache = {}

let type_port_map = {
    any: (ports, label, name, defaultValue, data = null) => {
        return ports.any({
            label,
            name,
            controls: [
                Controls.text({
                    label,
                    name,
                    defaultValue
                })
            ]
        })
    },
    int: (ports, label, name, defaultValue, data = null) => {
        return ports.number({
            label,
            name,
            controls: [
                Controls.number({
                    label,
                    name,
                    defaultValue
                })
            ]
        })
    },
    float: (ports, label, name, defaultValue, data = null) => {
        return ports.number({
            label,
            name,
            controls: [
                Controls.number({
                    label,
                    name,
                    defaultValue
                })
            ]
        })
    },
    number: (ports, label, name, defaultValue, data = null) => {
        return ports.number({
            label,
            name,
            controls: [
                Controls.number({
                    label,
                    name,
                    defaultValue
                })
            ]
        })
    },
    bool: (ports, label, name, defaultValue, data = null) => {
        return ports.boolean({
            label,
            name,
            controls: [
                Controls.checkbox({
                    label,
                    name,
                    defaultValue
                })
            ]
        })
    },
    boolean: (ports, label, name, defaultValue, data = null) => {
        return ports.boolean({
            label,
            name,
            controls: [
                Controls.checkbox({
                    label,
                    name,
                    defaultValue
                })
            ]
        })
    },
    str: (ports, label, name, defaultValue, data = null) => {
        return ports.string({
            label,
            name,
            controls: [
                Controls.text({
                    label,
                    name,
                    defaultValue
                })
            ]
        })
    },
    string: (ports, label, name, defaultValue, data = null) => {
        return ports.string({
            label,
            name,
            controls: [
                Controls.text({
                    label,
                    name,
                    defaultValue
                })
            ]
        })
    },
    tuple: (ports, label, name, defaultValue, data = null) => {
        return ports.tuple({
            label,
            name,
        })
    },
    dict: (ports, label, name, defaultValue, data = null) => {
        return ports.dict({
            label,
            name,
        })
    },
    control: (ports, label, name, defaultValue, data = null) => {
        return ports.control({
            label: "控制",
            name: "control",
        })
    },
    ["jupyterlab_nodeeditor.select.select"]: (ports, label, name, defaultValue, data = null) => {
        return ports.select({
            label,
            name,
            controls: [
                Controls.select({
                    name,
                    label,
                    defaultValue,
                    options: data
                })
            ]
        })
    },
    ["jupyterlab_nodeeditor.select.mselect"]: (ports, label, name, defaultValue, data = null) => {
        return ports.mselect({
            label,
            name,
            controls: [
                Controls.multiselect({
                    name,
                    label,
                    defaultValue,
                    options: data
                })
            ]
        })
    },
    ["jupyterlab_nodeeditor.slider.slider"]: (ports, label, name, defaultValue, data = {
        min: 0,
        max: 1,
        step: 0.1
    }) => {
        return ports.slider({
            label,
            name,
            color: Colors.slider,
            controls: [
                Controls.custom({
                    name: "value",
                    label: label,
                    defaultValue: { value: defaultValue || 0, ...data },
                    render: (data,
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        const inputRef = useRef<HTMLInputElement>(null)
                        const [curType, setCurType] = useState('range')
                        useEffect(() => {
                            if (inputRef.current) {
                                inputRef.current.value = data.value.toString()
                            }
                        }, [])
                        return <span>
                            <label>{label}</label>
                            <input
                                style={{
                                    verticalAlign: 'middle'
                                }}
                                ref={inputRef}
                                type={curType}
                                min={data.min}
                                max={data.max}
                                step={data.step}
                                onMouseDown={e => e.stopPropagation()}
                                onChange={e => {
                                    data.value =
                                        Number(e.target.value)
                                    onChange({ ...data })
                                }}
                                onDoubleClick={e => {
                                    setCurType('number')
                                }}
                                onBlur={e => {
                                    setCurType('range')
                                }}
                            />
                            {curType == 'range' && <output style={{
                                fontSize: '16',
                                verticalAlign: 'middle',
                            }}>{data.value}</output>}
                        </span>
                    }
                })
            ]
        })
    }
}

let renderCache = {}

export function common_out(ports) {
    return [
        get_port_func("control")(ports),
        get_port_func("any")(ports, "输出", "out", "None")
    ]
}

export function get_port_func(name) {
    let port_func = type_port_map[name]
    if (!port_func) {
        port_func = type_port_map.any
    }
    return port_func
}

export function get_tuple_max_index(data) {
    let maxV = -1
    let i
    for (const key in data) {
        let ret = /v(\d)/g.exec(key)
        if (ret) {
            i = Number(ret[1])
            if (maxV < i) {
                maxV = i
            }
        }
    }
    return maxV
}

export function tuple_value_name(index) {
    return `v${index}`
}

export function set_port_control_value(targetElement, nodeId, port_name, value: any) {
    let selector = `[data-node-id='${nodeId}'][data-port-name='${port_name}']`
    let element = targetElement.querySelector(selector)
    if (!element || !element.parentElement) return false
    let port_type = element.getAttribute("data-port-type")
    switch (port_type) {
        case "string":
        case "any": {
            let textAreaElements = element.parentElement.getElementsByTagName("textarea")
            if (textAreaElements.length <= 0) return false
            let textAreaElement = textAreaElements[0] as HTMLTextAreaElement
            if (value) {
                textAreaElement.value = value
            }
            else {
                switch (port_type) {
                    case "any":
                        textAreaElement.value = "None"
                        break
                    case "string":
                        textAreaElement.value = ""
                        break
                }
            }
        } break
        case "boolean":
        case "number": {
            let inputElements = element.parentElement.getElementsByTagName("input")
            if (inputElements.length <= 0) return false
            let inputElement = inputElements[0] as HTMLInputElement
            switch (port_type) {
                case "boolean":
                    if (value) {
                        inputElement.checked = value
                    } else {
                        inputElement.checked = false
                    }
                    break
                case "number":
                    if (value) {
                        inputElement.value = `${value}`
                    } else {
                        inputElement.value = "0"
                    }
                    break
            }
        } break
    }
}

export function get_port_default_value(port_type) {
    switch (port_type) {
        case "dict":
            return "{}"
        case "tuple":
            return "()"
        case "any":
            return "None"
        case "int":
        case "float":
        case "number":
            return 0
        case "string":
            return ""
        case "bool":
        case "boolean":
            return false
    }
}

function make_dict_name(name, type) {
    return `${name}@${type}`
}

export function parse_dict_name(name) {
    return /(\S+?)@(\S+)/g.exec(name)
}

export default function createConfig() {
    const config = new FlumeConfig()
    config
        .addPortType({
            type: "any",
            name: "any",
            label: "任何类型",
            color: Colors.grey,
            acceptTypes: ["any",
                "string", "number",
                "boolean", "image",
                "select", "mselect",
                "video", "tuple", "dict"
            ],
            controls: [
                Controls.text({
                    name: "any",
                    label: "默认值",
                    defaultValue: "None"
                })
            ]
        })
        .addPortType({
            type: "string",
            name: "string",
            label: "文本(string/Text)",
            color: Colors.yellow,
            acceptTypes: ["any", "string",],
            controls: [
                Controls.text({
                    name: "string",
                    label: "文本(string/Text)"
                })
            ]
        })
        .addPortType({
            type: "boolean",
            name: "boolean",
            label: "是/否(True/False)",
            color: Colors.orange,
            acceptTypes: ["any", "boolean"],
            controls: [
                Controls.checkbox({
                    name: "boolean",
                    label: "是/否(True/False)"
                })
            ]
        })
        .addPortType({
            type: "number",
            name: "number",
            label: "数字",
            color: Colors.red,
            acceptTypes: ["any", "number"],
            controls: [
                Controls.number({
                    name: "number",
                    label: "数字",
                })
            ]
        })
        .addPortType({
            type: "jsstring",
            name: "jsstring",
            label: "文本(string/Text)",
            color: Colors.yellow,
            acceptTypes: ["any", "string",],
            controls: [
                Controls.text({
                    name: "string",
                    label: "文本(string/Text)"
                })
            ]
        })
        .addPortType({
            type: "image",
            name: "image",
            label: "图片",
            color: Colors.pink,
            acceptTypes: ["string", "any", "image"],
            controls: [
                Controls.custom({
                    name: "image",
                    label: "image",
                    defaultValue: {
                        urls: [],
                        index: 0
                    },
                    render: (data,
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        const get_url = () => {
                            if (typeof data.urls != "object") {
                                data.urls = [""]
                                data.index = 0
                                onChange({ urls: data.urls, index: 0 })
                            }
                            let urls = data.urls || []
                            let index = data.index || 0
                            if (urls.length == 0) {
                                return
                            }
                            return urls[index]
                        }
                        image_urls_functions[portProps.nodeId] = (urls) => {
                            onChange({ urls, index: 0 })
                        }

                        function showImg() {
                            executionContext.setShowImgUrls(data.urls)
                            executionContext.setShowImgStartIndex(data.index)
                            executionContext.setShowImg(true)
                        }

                        const onLoad = (e) => {
                            try {
                                executionContext.updateNodeConnections(portProps.nodeId)
                            } catch (error) {

                            }
                        }

                        const [showImagePosition, setImagePosition] = useState(false)
                        const positionRef = React.useRef(null)
                        const imageRef = React.useRef(null)
                        const rectSelect = React.useRef(false)
                        interface positionRecord {
                            x: number,
                            y: number
                        }
                        const startPos = React.useRef<null | positionRecord>(null)
                        const selectRect = React.useRef<null | SVGPathElement>(null)

                        const getMousePos = (clientX, clientY) => {
                            const imgElement = imageRef.current as unknown as HTMLImageElement
                            const scale = executionContext.editorOptions["stagetScale"]
                            const rect = imgElement.getBoundingClientRect()
                            let posX = (clientX - rect.x) / scale
                            let posY = (clientY - rect.y) / scale
                            let imgPosX = Math.floor(posX / (rect.width / scale) * imgElement.naturalWidth)
                            let imgPosY = Math.floor(posY / (rect.height / scale) * imgElement.naturalHeight)
                            return { posX, posY, imgPosX, imgPosY }
                        }


                        const updatePostionInfo = (e: React.MouseEvent<HTMLImageElement, MouseEvent>) => {
                            if (!positionRef.current || !imageRef.current) {
                                return
                            }
                            const imgElement = imageRef.current as unknown as HTMLImageElement
                            const element = positionRef.current as unknown as HTMLSpanElement
                            let { posX, posY, imgPosX, imgPosY } = getMousePos(e.clientX, e.clientY)

                            element.style.position = 'absolute'
                            element.style.left = `${posX}px`
                            element.style.top = `${posY}px`

                            if (rectSelect.current && startPos.current) {
                                let startPosData = getMousePos(startPos.current.x, startPos.current.y)
                                element.innerText = `[${startPosData.imgPosX}, ${startPosData.imgPosY}, ${imgPosX}, ${imgPosY}]`
                            } else {
                                element.innerText = `[${imgPosX}, ${imgPosY}]`
                            }

                            if (imgPosX < 0
                                || imgPosX >= imgElement.naturalWidth
                                || imgPosY < 0
                                || imgPosY >= imgElement.naturalHeight) {
                                setImagePosition(false)
                            }
                        }

                        const updateRectSelct = (e: React.MouseEvent<HTMLImageElement, MouseEvent>) => {
                            if (!selectRect.current) {
                                const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                                svg.setAttribute("class", SvgContainerStyle);
                                svg.setAttribute("style", "z-index:100;");
                                svg.setAttribute("viewport", `0 0 `)
                                const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                                path.setAttribute("stroke", "rgb(185, 186, 189)");
                                path.setAttribute("stroke-width", "1");
                                path.setAttribute("stroke-linecap", "round");
                                path.setAttribute("fill", "rgba(255,255,255,0.2)");
                                path.setAttribute("d", "");
                                svg.appendChild(path)
                                if (imageRef.current) {
                                    let container = imageRef.current as unknown as HTMLImageElement
                                    if (container.parentElement) {
                                        container.parentElement.appendChild(svg)
                                    }
                                }
                                selectRect.current = path
                            }

                            if (selectRect.current && startPos.current) {
                                const imgElement = imageRef.current as unknown as HTMLImageElement
                                const rect = imgElement.getBoundingClientRect()
                                const scale = executionContext.editorOptions["stagetScale"]
                                let startPosRecord = startPos.current as positionRecord
                                let startPosX = (startPosRecord.x - rect.x) / scale
                                let startPosY = (startPosRecord.y - rect.y) / scale
                                let endPosX = (e.clientX - rect.x) / scale
                                let endPosY = (e.clientY - rect.y) / scale
                                let width = endPosX - startPosX
                                let height = endPosY - startPosY
                                selectRect.current.setAttribute("d", `M ${startPosX} ${startPosY} h ${width} v ${height} h ${-width} Z`)
                            }
                        }

                        const handleOnMouseEnter = (e: React.MouseEvent<HTMLImageElement, MouseEvent>) => {
                            setImagePosition(true)
                            updatePostionInfo(e)
                        }

                        const handleOnMouseMove = (e: React.MouseEvent<HTMLImageElement, MouseEvent>) => {
                            if (!showImagePosition) {
                                return
                            }

                            if (rectSelect.current) {
                                updateRectSelct(e)
                            }

                            updatePostionInfo(e)
                        }

                        const handleOnMouseLeave = (e: React.MouseEvent<HTMLImageElement, MouseEvent>) => {
                            setImagePosition(false)
                        }

                        const handleOnMouseDownUP = (e: React.MouseEvent<HTMLDivElement, MouseEvent>, down: boolean) => {
                            switch (e.button) {
                                case 2:
                                    rectSelect.current = down
                                    if (!down) {
                                        startPos.current = null
                                        const element = positionRef.current as unknown as HTMLSpanElement
                                        navigator.clipboard.writeText(element.innerText).then(() => {
                                            Notification.success(`复制选取到剪切板成功${element.innerText}`)
                                        }).catch(reason => {
                                            Notification.error("复制选取到剪切板错误！")
                                        })
                                    } else {
                                        startPos.current = {
                                            x: e.clientX,
                                            y: e.clientY
                                        }
                                        if (selectRect.current) {
                                            selectRect.current.setAttribute('d', "")
                                        }
                                    }
                                    break;
                            }
                        }

                        return (
                            <div>
                                <button onClick={showImg}>浏览</button>
                                <button onClick={e => {
                                    const link = document.createElement('a');
                                    link.href = get_url();
                                    link.download = 'image.png';
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                }}>下载</button>
                                <button onClick={e => {
                                    let new_index = (data.index - 1 + data.urls.length) % data.urls.length
                                    onChange({ urls: data.urls, index: new_index })
                                }}>《</button>
                                <button onClick={e => {
                                    let new_index = (data.index + 1) % data.urls.length
                                    onChange({ urls: data.urls, index: new_index })
                                }}>》</button>
                                <button onClick={e => {
                                    navigator.clipboard.writeText(get_url())
                                }}>复制url</button>
                                <div
                                    style={{
                                        position: 'relative',
                                        top: '0px',
                                        left: '0px'
                                    }}
                                    onMouseEnter={handleOnMouseEnter}
                                    onMouseMove={handleOnMouseMove}
                                    onMouseLeave={handleOnMouseLeave}
                                    onMouseDown={e => handleOnMouseDownUP(e, true)}
                                    onMouseUp={e => handleOnMouseDownUP(e, false)}
                                >
                                    <img
                                        style={{
                                            width: '100%',
                                            height: "100%",
                                            objectFit: 'contain',
                                        }}
                                        onLoad={onLoad}
                                        onDoubleClick={showImg}
                                        id={"img_" + portProps.nodeId}
                                        ref={imageRef}
                                        src={get_url()}
                                    />
                                    {
                                        showImagePosition && <span
                                            ref={positionRef}
                                            style={{
                                                position: 'absolute',
                                                backgroundColor: 'white',
                                            }}
                                        ></span>
                                    }
                                </div>
                                <span style={{ color: 'white' }}>索引:{data.index}</span>
                            </div>
                        )
                    }
                }),
            ]
        })
        .addPortType({
            type: "video",
            name: "video",
            label: "视频",
            color: Colors.pink,
            acceptTypes: ["string", "any", "video"],
            controls: [
                Controls.custom({
                    name: "video",
                    label: "video",
                    defaultValue: {
                        urls: [],
                        index: 0
                    },
                    render: (data,
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        const get_url = () => {
                            if (typeof data.urls != "object") {
                                data.urls = [""]
                                data.index = 0
                                onChange({ urls: data.urls, index: 0 })
                            }
                            let urls = data.urls || []
                            let index = data.index || 0
                            if (urls.length == 0) {
                                return
                            }
                            return urls[index]
                        }

                        image_urls_functions[portProps.nodeId] = (urls) => {
                            onChange({ urls, index: 0 })
                        }

                        const onLoad = (e) => {
                            executionContext.updateNodeConnections(portProps.nodeId)
                        }

                        return (
                            <div>
                                <button onClick={e => {
                                    const link = document.createElement('a');
                                    link.href = get_url();
                                    link.download = 'image.png';
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                }}>下载</button>
                                <button onClick={e => {
                                    let new_index = (data.index - 1 + data.urls.length) % data.urls.length
                                    onChange({ urls: data.urls, index: new_index })
                                }}>《</button>
                                <button onClick={e => {
                                    let new_index = (data.index + 1) % data.urls.length
                                    onChange({ urls: data.urls, index: new_index })
                                }}>》</button>
                                <button onClick={e => {
                                    navigator.clipboard.writeText(get_url())
                                }}>复制url</button>
                                <video
                                    onLoad={onLoad}
                                    controls
                                    id={"vedio_" + portProps.nodeId}
                                    style={{ width: "100%" }}
                                    src={get_url()}
                                />
                                <span>当前索引:{data.index}</span>
                            </div>
                        )
                    }
                }),
            ]
        })
        .addPortType({
            type: "select",
            name: "select",
            label: "select",
            color: Colors.purple,
            acceptTypes: ["any", "select"],
            controls: [
            ]
        })
        .addPortType({
            type: "mselect",
            name: "mselect",
            label: "mselect",
            color: Colors.blue,
            acceptTypes: ["any", "mselect"],
            controls: [
                Controls.multiselect({
                    name: "mselect",
                    label: "mselect",
                    options: [
                        { value: "red", label: "Red" },
                        { value: "blue", label: "Blue" },
                        { value: "yellow", label: "Yellow" },
                        { value: "green", label: "Green" },
                        { value: "orange", label: "Orange" },
                        { value: "purple", label: "Purple" },
                    ]
                })
            ]
        })
        .addPortType({
            type: "tuple",
            name: "tuple",
            label: "tuple",
            color: Colors.tuple,
            acceptTypes: ["any", "tuple"],
            controls: []
        })
        .addPortType({
            type: "dict",
            name: "dict",
            label: "dict",
            color: Colors.dict,
            acceptTypes: ["any", "dict"],
            controls: []
        })
        .addPortType({
            type: "control",
            name: "control",
            label: "",
            color: Colors.control,
            acceptTypes: ["control"],
            controls: []
        })
        .addPortType({
            type: "tuple_editor",
            name: "tuple_editor",
            label: "tuple_editor",
            color: Colors.tuple,
            acceptTypes: [],
            hidePort: true,
            controls: [
                Controls.number({
                    name: "index",
                    label: "index"
                }),
                Controls.select({
                    name: "type",
                    label: "type",
                    defaultValue: "any",
                    options: [
                        { value: "number", label: "数字" },
                        { value: "string", label: "字符串" },
                        { value: "bool", label: "布尔" },
                        { value: "any", label: "任意" },
                    ]
                }),
                Controls.custom({
                    name: "tuple_editor",
                    label: "tuple_editor",
                    defaultValue: [],
                    render: (data: any[],
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        function insertAt(data: any[], index: number, value: any) {
                            data.splice(index, 0, value);
                            // 移动value
                            let node = executionContext.editorNodes[portProps.nodeId]
                            if (node) {
                                let maxV = get_tuple_max_index(node.inputData)
                                let inputData = node.inputData
                                let tmp
                                for (let i = maxV; i >= index; i--) {
                                    try {
                                        tmp = inputData[tuple_value_name(i)]
                                        if (tmp) {
                                            inputData[tuple_value_name(i + 1)] = {
                                                [tuple_value_name(i + 1)]: tmp[tuple_value_name(i)]
                                            }
                                        }
                                        else {
                                            delete inputData[tuple_value_name(i + 1)]
                                        }
                                    } catch (error) { }
                                }
                                try { delete inputData[tuple_value_name(index)] } catch (error) { }
                                console.log(inputData)
                            }
                        }
                        function removeAt(data: any[], index: number) {
                            data.splice(index, 1);
                            // 移动value
                            let node = executionContext.editorNodes[portProps.nodeId]
                            if (node) {
                                let inputData = node.inputData
                                let maxV = get_tuple_max_index(inputData)
                                let tmp
                                for (let i = index; i < maxV; i++) {
                                    tmp = inputData[tuple_value_name(i + 1)]
                                    if (tmp) {
                                        inputData[tuple_value_name(i)] = {
                                            [tuple_value_name(i)]: tmp[tuple_value_name(i + 1)]
                                        }
                                    } else {
                                        delete inputData[tuple_value_name(i)]
                                    }
                                }
                                delete inputData[tuple_value_name(maxV)]
                                console.log(inputData)
                            }
                        }
                        return (
                            <div>
                                <button onClick={e => {
                                    insertAt(data, allData.index, allData.type)
                                    onChange(data)
                                }}>添加+</button>
                                <button onClick={e => {
                                    removeAt(data, allData.index)
                                    onChange(data)
                                }}>删除-</button>
                            </div>
                        )
                    }
                }),
            ]
        })
        .addPortType({
            type: "dict_editor",
            name: "dict_editor",
            label: "dict_editor",
            color: Colors.dict,
            acceptTypes: [],
            hidePort: true,
            controls: [
                Controls.text({
                    name: "name",
                    label: "name"
                }),
                Controls.select({
                    name: "type",
                    label: "type",
                    defaultValue: "any",
                    options: [
                        { value: "number", label: "数字" },
                        { value: "string", label: "字符串" },
                        { value: "bool", label: "布尔" },
                        { value: "any", label: "任意" },
                    ]
                }),
                Controls.custom({
                    name: "dict_editor",
                    label: "dict_editor",
                    defaultValue: {},
                    render: (data: {},
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        return (
                            <div>
                                <button onClick={e => {
                                    data[allData["name"]] = allData["type"]
                                    onChange({ ...data })
                                }}>添加+</button>
                                <button onClick={e => {
                                    delete data[allData["name"]]
                                    // 删除data
                                    let node = executionContext.editorNodes[portProps.nodeId]
                                    if (node) {
                                        delete node.inputData[allData["name"]]
                                    }
                                    onChange({ ...data })
                                }}>删除-</button>
                            </div>
                        )
                    }
                }),
            ]
        })
        .addPortType({
            type: "operator",
            name: "operator",
            label: "运算符",
            color: Colors.purple,
            acceptTypes: [],
            hidePort: true,
            controls: [
                Controls.select({
                    name: "operator",
                    label: "运算符",
                    defaultValue: "+",
                    options: [
                        {
                            "value": "+",
                            "label": "加法运算符(+)"
                        },
                        {
                            "value": "-",
                            "label": "减法运算符(-)"
                        },
                        {
                            "value": "*",
                            "label": "乘法运算符(*)"
                        },
                        {
                            "value": "/",
                            "label": "除法运算符(/) "
                        },
                        {
                            "value": "%",
                            "label": "取余运算符(%)"
                        },
                        {
                            "value": "**",
                            "label": "幂运算符(**)"
                        },
                        {
                            "value": "//",
                            "label": "整除运算符(//)"
                        },
                        {
                            "value": "=",
                            "label": "赋值运算符(=)"
                        },
                        {
                            "value": ">",
                            "label": "大于运算符(>)"
                        },
                        {
                            "value": "<",
                            "label": "小于运算符(<)"
                        },
                        {
                            "value": ">=",
                            "label": "大于等于运算符(>=)"
                        },
                        {
                            "value": "<=",
                            "label": "小于等于运算符(<=)"
                        },
                        {
                            "value": "==",
                            "label": "等于运算符(==)"
                        },
                        {
                            "value": "!=",
                            "label": "不等于运算符(!=)"
                        },
                        {
                            "value": "and",
                            "label": "逻辑与运算符(and)"
                        },
                        {
                            "value": "or",
                            "label": "逻辑或运算符(or)"
                        },
                        {
                            "value": "not",
                            "label": "逻辑非运算符(not)"
                        },
                        {
                            "value": "~",
                            "label": "按位取反运算符(~)"
                        },
                        {
                            "value": "|",
                            "label": "按位或运算符(|)"
                        },
                        {
                            "value": "&",
                            "label": "按位与运算符(&)"
                        },
                        {
                            "value": "^",
                            "label": "按位异或运算符(^)"
                        },
                        {
                            "value": ">>",
                            "label": "右移运算符(>>)"
                        },
                        {
                            "value": "<<",
                            "label": "左移运算符(<<)"
                        },
                        {
                            "value": "in",
                            "label": "成员运算符(in)"
                        },
                        {
                            "value": "not in",
                            "label": "非成员运算符(not in)"
                        },
                        {
                            "value": "is",
                            "label": "身份运算符(is)"
                        },
                        {
                            "value": "is not",
                            "label": "非身份运算符(is not)"
                        },
                        {
                            "value": "[]",
                            "label": "取值[key]"
                        }
                    ]
                }),
            ]
        })
        .addPortType({
            type: "code_editor",
            name: "code_editor",
            label: "code_editor",
            color: Colors.dict,
            acceptTypes: [],
            hidePort: true,
            controls: [
                Controls.custom({
                    name: "code_editor",
                    label: "",
                    defaultValue: {},
                    render: (data: {},
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        const editorContainerRef = React.useRef(null)
                        const editorRef = React.useRef<null | monaco.editor.IStandaloneCodeEditor>(null)
                        const [showEditor, setShowEditor] = React.useState(false)
                        React.useEffect(() => {
                            if (showEditor) {
                                editorRef.current = monaco.editor.create(
                                    editorContainerRef.current as unknown as HTMLElement, {
                                    theme: "vs-dark",
                                    language: "python",
                                })
                                let editor = editorRef.current as monaco.editor.IStandaloneCodeEditor
                                editor.layout()
                                editor.onDidFocusEditorWidget(e => {
                                    executionContext.setInputing(true)
                                })
                                editor.onDidBlurEditorWidget(e => {
                                    executionContext.setInputing(false)
                                })
                            }
                        }, [showEditor])
                        return (
                            <div style={{
                                width: "100%"
                            }}>
                                <button onClick={e => {
                                    setShowEditor(!showEditor)
                                }}>{showEditor ? '完成' : '编辑'}</button>
                                {
                                    showEditor && <div ref={editorContainerRef}
                                        style={{
                                            width: "100%",
                                            height: "400px"
                                        }}
                                    ></div>
                                }

                            </div>
                        )
                    }
                }),
            ]
        })
        .addPortType({
            type: "text_editor",
            name: "text_editor",
            label: "文本",
            color: Colors.yellow,
            acceptTypes: ['any', 'string', 'text_editor'],
            controls: [
                Controls.custom({
                    name: "value",
                    label: "",
                    defaultValue: {
                        value: "",
                        showEditor: false
                    },
                    render: (data,
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        const editorContainerRef = React.useRef(null)
                        const editorRef = React.useRef<null | monaco.editor.IStandaloneCodeEditor>(null)
                        const [showEditor, setShowEditor] = React.useState(data.showEditor)

                        React.useEffect(() => {
                            if (showEditor) {
                                editorRef.current = monaco.editor.create(
                                    editorContainerRef.current as unknown as HTMLElement, {
                                    theme: "vs-dark",
                                })
                                let editor = editorRef.current as monaco.editor.IStandaloneCodeEditor
                                editor.layout()
                                editor.onDidFocusEditorWidget(e => {
                                    executionContext.setInputing(true)
                                })
                                editor.onDidBlurEditorWidget(e => {
                                    executionContext.setInputing(false)
                                })
                                editor.setValue(data.value)
                                editor.onDidChangeModelContent(e => {
                                    onChange({
                                        value: editorRef.current?.getValue(),
                                        showEditor
                                    })
                                })
                                editor.onMouseDown(e => {
                                    e.event.stopPropagation()
                                })
                            }
                            if (showEditor != data.showEditor) {
                                onChange({ ...data, showEditor })
                            }
                        }, [showEditor])
                        return (
                            <div style={{
                                width: "100%"
                            }}>
                                <button onClick={e => {
                                    setShowEditor(!showEditor)
                                }}>{showEditor ? '关闭' : '编辑'}</button>
                                {
                                    showEditor && <div ref={editorContainerRef}
                                        style={{
                                            width: "100%",
                                            height: "400px"
                                        }}
                                    ></div>
                                }
                            </div>
                        )
                    }
                }),
            ]
        })
        .addPortType({
            type: "text_viewer",
            name: "text_viewer",
            label: "文本",
            color: Colors.yellow,
            acceptTypes: ['any', 'string', 'text_viewer'],
            controls: [
                Controls.custom({
                    name: "value",
                    label: "",
                    defaultValue: {
                        showText: false,
                        value: ''
                    },
                    render: (data,
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        const viewerContainerRef = React.useRef<HTMLTextAreaElement>(null)
                        const [showText, setshowText] = React.useState(data.showText)

                        text_viewer_text_functions[portProps.nodeId] = (text) => {
                            onChange({ ...data, value: text })
                            if (showText && viewerContainerRef.current) {
                                viewerContainerRef.current.value = text
                            }
                        }

                        React.useEffect(() => {
                            if (showText && viewerContainerRef.current) {
                                viewerContainerRef.current.value = data.value
                            }
                            if (data.showText != showText) {
                                onChange({ ...data, showText })
                            }
                        }, [showText])

                        const handlePossibleResize = e => {
                            e.stopPropagation();
                        };

                        return (
                            <div style={{
                                width: "100%"
                            }}>
                                <button onClick={e => {
                                    setshowText(!showText)
                                }}>{showText ? '关闭' : '显示'}</button>
                                <button onClick={e => {
                                    if (viewerContainerRef.current) {
                                        navigator.clipboard.writeText(viewerContainerRef.current.value)
                                    }
                                }}>复制</button>
                                {
                                    showText && <textarea ref={viewerContainerRef}
                                        onMouseDown={handlePossibleResize}
                                        onContextMenu={e => e.stopPropagation()}
                                        onKeyDown={e => e.stopPropagation()}
                                        onKeyUp={e => e.stopPropagation()}
                                        style={{
                                            width: "100%",
                                            height: "400px",
                                            backgroundColor: '#292C33',
                                            fontSize: '20px',
                                            color: 'white'
                                        }}
                                        readOnly={true}
                                    ></textarea>
                                }
                            </div>
                        )
                    }
                }),
            ]
        })
        .addPortType({
            type: "color_picker",
            name: "color_picker",
            label: "颜色",
            color: Colors.black,
            acceptTypes: ['any', 'string', 'color_picker'],
            controls: [
                Controls.custom({
                    name: "value",
                    label: "",
                    defaultValue: { value: '#000000' },
                    render: (data,
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        const [color, setColor] = useState(data.color);

                        const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                            setColor(e.target.value);
                            onChange({
                                value: e.target.value
                            });
                        }
                        return (
                            <div>
                                <input
                                    type="color"
                                    value={color}
                                    onChange={handleChange}
                                />
                            </div>
                        );
                    }
                }),
            ]
        })
        .addPortType({
            type: "curve_editor",
            name: "curve_editor",
            label: "曲线编辑器",
            color: Colors.curve_editor,
            acceptTypes: ['any', 'curve_editor'],
            controls: [
                Controls.custom({
                    name: "value",
                    label: "",
                    defaultValue: { value: [] },
                    render: (data,
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        function diffurent(points) {
                            if (points.length == data.value.length) {
                                for (let index = 0; index < points.length; index++) {
                                    let savedValue = data.value[index]
                                    let curValue = points[index]
                                    if (savedValue.x != curValue.x || savedValue.y != curValue.y) {
                                        return true
                                    }
                                }
                            } else {
                                return true
                            }
                            return false
                        }
                        return <CurveEditor
                            points={data.value}
                            onChange={(points) => {
                                if (diffurent(points)) {
                                    onChange({ value: points })
                                }
                            }}
                        />
                    }
                }),
            ]
        })
        .addPortType({
            type: "slider",
            name: "slider",
            label: "滑块",
            color: Colors.slider,
            acceptTypes: ['any', 'number', 'slider'],
            controls: [
                Controls.custom({
                    name: "value",
                    label: "",
                    defaultValue: { value: 0, min: 0, max: 1, step: 0.1 },
                    render: (data,
                        onChange,
                        executionContext: NodeEditorWidget,
                        triggerRecalculation,
                        portProps, allData) => {
                        return <input type="range"
                            value={data.value}
                            min={data.min}
                            max={data.max}
                            step={data.step}
                            onMouseDown={e => e.stopPropagation()}
                            onChange={e => {
                                onChange({ value: e.target.value, ...data })
                            }} />
                    }
                }),
            ]
        })
        .addNodeType({
            type: "image",
            label: "图片显示(show image)",
            description: "图片显示(show image)",
            initialWidth: 250,
            inputs: ports => [
                get_port_func("control")(ports),
                get_port_func("string")(ports, "url列表", "urls"),
                ports.image({ hidePort: true })

            ],
            outputs: common_out
        })
        .addNodeType({
            type: "video",
            label: "视频(show video)",
            description: "视频(show video)",
            initialWidth: 250,
            inputs: ports => [
                get_port_func("control")(ports),
                get_port_func("string")(ports, "url列表", "urls"),
                ports.video({ hidePort: true })

            ],
            outputs: common_out
        })
        .addNodeType({
            type: "any",
            label: "任意类型(any)",
            description: "任意类型(any)",
            initialWidth: buildNodeWidth("any", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("control")(ports),
                get_port_func("any")(ports, "值", "value", "None")
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "tuple",
            label: "元组(tuple)",
            description: "元组(tuple)",
            initialWidth: 250,
            inputs: ports => (inputData, connections, executionContext: NodeEditorWidget, nodeId) => {
                let ret: any[] = [get_port_func("control")(ports), ports.tuple_editor()]
                let index = 0
                if (inputData.tuple_editor && inputData.tuple_editor.tuple_editor) {
                    for (const port_type of inputData.tuple_editor.tuple_editor) {
                        let port_func = get_port_func(port_type)
                        let name = tuple_value_name(index++)
                        let target_value = get_port_default_value(port_type)
                        let port = port_func(ports, name, name, target_value)
                        ret.push(port)
                    }

                    let cache = tupleCache[nodeId]
                    if (!cache || cache.length != inputData.tuple_editor.tuple_editor.length) {
                        setTimeout(() => {
                            let index = 0
                            for (const port_type of inputData.tuple_editor.tuple_editor) {
                                let name = tuple_value_name(index++)
                                set_port_control_value(executionContext.node, nodeId, name,
                                    inputData[name] ? inputData[name][name] : null)
                            }
                        })
                    }

                    tupleCache[nodeId] = JSON.parse(JSON.stringify(inputData.tuple_editor.tuple_editor))
                }
                return ret
            },
            outputs: common_out,
        })
        .addNodeType({
            type: "dict",
            label: "字典(dict)",
            description: "字典(dict)",
            initialWidth: 250,
            inputs: ports => (inputData, connections, executionContext: NodeEditorWidget, nodeId) => {
                let ret: any[] = [get_port_func("control")(ports), ports.dict_editor()]
                if (inputData.dict_editor && inputData.dict_editor.dict_editor) {
                    let port_data = inputData.dict_editor.dict_editor
                    let port_type
                    let resetData = false
                    let cache = dictCache[nodeId]
                    let tmp_name
                    for (const name in port_data) {
                        port_type = port_data[name]
                        let port_func = get_port_func(port_type)
                        let target_value = get_port_default_value(port_type)
                        tmp_name = make_dict_name(name, port_type)
                        let port = port_func(ports, tmp_name, tmp_name, target_value)
                        ret.push(port)
                        if (cache && (!cache[name] || cache[name] != port_type)) {
                            resetData = true
                        }
                    }

                    if (cache && !resetData) {
                        for (const name in cache) {
                            if (!port_data[name] || cache[name] != port_data[name]) {
                                resetData = true
                            }
                        }
                    }

                    if (!cache || resetData) {
                        setTimeout(() => {
                            for (const name in inputData.dict_editor.dict_editor) {
                                tmp_name = make_dict_name(name, port_type)
                                set_port_control_value(executionContext.node, nodeId, tmp_name,
                                    inputData[tmp_name] ? inputData[tmp_name][tmp_name] : null)
                            }
                        })
                    }
                    dictCache[nodeId] = JSON.parse(JSON.stringify(inputData.dict_editor.dict_editor))
                }
                return ret
            },
            outputs: common_out,
        })
        .addNodeType({
            type: "int",
            label: "整数(int)",
            description: "整数(int)",
            initialWidth: buildNodeWidth("int", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("control")(ports),
                get_port_func("str")(ports, "值", "value", 0)
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "float",
            label: "浮点数(float)",
            description: "浮点数(float)",
            initialWidth: buildNodeWidth("float", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("control")(ports),
                get_port_func("str")(ports, "值", "value", 0)
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "string",
            label: "文本/字符串(string)",
            description: "文本/字符串(string)",
            initialWidth: 500,
            inputs: ports => [
                get_port_func("control")(ports),
                ports.text_editor({ name: 'value', hidePort: true })
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "show string",
            label: "显示文本(show string)",
            description: "显示文本(show string)",
            initialWidth: 500,
            inputs: ports => [
                get_port_func("control")(ports),
                get_port_func("any")(ports, "输入", "input", "None"),
                ports.text_viewer({ name: 'value', hidePort: true })
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "bool",
            label: "布尔(bool)(真/假)",
            description: "布尔(bool)(真/假)",
            initialWidth: buildNodeWidth("bool", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("control")(ports),
                get_port_func("bool")(ports, "值", "value", 0)
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "if",
            label: "条件判定(if)",
            description: "条件判定(if)",
            initialWidth: buildNodeWidth("if", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("bool")(ports, "判定", "value", 0),
                get_port_func("any")(ports, "真", "true", "None"),
                get_port_func("any")(ports, "假", "false", "None"),
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "loop",
            label: "循环(loop)",
            description: "循环(loop)",
            initialWidth: buildNodeWidth("loop", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("control")(ports),
                get_port_func("bool")(ports, "判定", "value", 0),
                ports.control({ label: "循环", name: "loop" }),
            ],
            outputs: ports => [
                get_port_func("control")(ports),
            ]
        })
        .addNodeType({
            type: "operator",
            label: "操作符(operator)",
            description: "操作符(operator)",
            initialWidth: buildNodeWidth("operator", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("control")(ports),
                ports.operator(),
                get_port_func("any")(ports, "参数1", "value1", "None"),
                get_port_func("any")(ports, "参数2", "value2", "None"),
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "setvar",
            label: "设置变量(setvar)",
            description: "设置变量(setvar)",
            initialWidth: buildNodeWidth("设置变量(setvar)", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("control")(ports),
                get_port_func("any")(ports, "变量名", "name", ""),
                get_port_func("any")(ports, "值", "value", "None"),
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "start",
            label: "开始(start)",
            description: "开始(start)",
            initialWidth: buildNodeWidth("开始(start)", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("control")(ports),
            ],
            outputs: [],
        })
        .addNodeType({
            type: "on_data_change",
            label: "前置数据变更(on_data_change)",
            description: "前置数据变更(on_data_change)",
            initialWidth: buildNodeWidth("前置数据变更(on_data_change)", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                get_port_func("control")(ports),
            ],
            outputs: [],
        })
        .addNodeType({
            type: "color",
            label: "颜色(color)",
            description: "颜色(color)",
            initialWidth: buildNodeWidth("颜色(color)", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                ports.color_picker({ name: 'value', hidePort: true })
            ],
            outputs: common_out,
        })
        .addNodeType({
            type: "curve",
            label: "曲线(curve)",
            description: "曲线(curve)",
            initialWidth: buildNodeWidth("曲线(curve)", headerFontsize, nodeMinWidth, nodeMaxWidth),
            inputs: ports => [
                ports.curve_editor({ name: 'value', hidePort: true })
            ],
            outputs: common_out,
        })
    // .addNodeType({
    //     type: "function",
    //     label: "函数(function)",
    //     description: "函数(function)",
    //     initialWidth: 500,
    //     inputs: ports => [
    //         get_port_func("control")(ports),
    //         ports.code_editor()

    //     ],
    //     outputs: [],
    // })

    return config
}