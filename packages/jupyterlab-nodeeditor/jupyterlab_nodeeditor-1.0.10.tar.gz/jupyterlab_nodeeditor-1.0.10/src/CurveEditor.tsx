import React, { useState, useEffect, useMemo, useRef } from 'react';
interface Point {
    x: number,
    y: number
}

function getCControlPoints(P0: Point, Bt1: Point, Bt2: Point, P3: Point, t1 = 1 / 3, t2 = 2 / 3) {
    let v1x = Bt1.x - Math.pow(1 - t1, 3) * P0.x - Math.pow(t1, 3) * P3.x
    let v1y = Bt1.y - Math.pow(1 - t1, 3) * P0.y - Math.pow(t1, 3) * P3.y
    let v2x = Bt2.x - Math.pow(1 - t2, 3) * P0.x - Math.pow(t2, 3) * P3.x
    let v2y = Bt2.y - Math.pow(1 - t2, 3) * P0.y - Math.pow(t2, 3) * P3.y

    let a = 3 * Math.pow(1 - t1, 2) * t1
    let b = 3 * (1 - t1) * Math.pow(t1, 2)
    let c = 3 * Math.pow(1 - t2, 2) * t2
    let d = 3 * (1 - t2) * Math.pow(t2, 2)

    let p1X = (v1x * d - v2x * b) / (a * d - b * c)
    let p1Y = (v1y * d - v2y * b) / (a * d - b * c)
    let p2X = (v1x * c - v2x * a) / (b * c - a * d)
    let p2Y = (v1y * c - v2y * a) / (b * c - a * d)

    return [{ x: p1X, y: p1Y }, { x: p2X, y: p2Y }]
}

function getSControlPoint(p0: Point, c1: Point, bt2: Point, p3: Point, t = 2 / 3) {
    let retX = (bt2.x - Math.pow(1 - t, 3) * p0.x - 3 * Math.pow(1 - t, 2) * t * c1.x - Math.pow(t, 3) * p3.x) / (3 * (1 - t) * Math.pow(t, 2))
    let retY = (bt2.y - Math.pow(1 - t, 3) * p0.y - 3 * Math.pow(1 - t, 2) * t * c1.y - Math.pow(t, 3) * p3.y) / (3 * (1 - t) * Math.pow(t, 2))
    return { x: retX, y: retY };
}

// 计算两点距离
function distance(p1: Point, p2: Point) {
    return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
}

function getQControlPoint(start: Point, end: Point, random: Point, t = 0.5) {
    let retX = (random.x - Math.pow((1 - t), 2) * start.x - Math.pow(t, 2) * end.x) / (2 * (1 - t) * t);
    let retY = (random.y - Math.pow((1 - t), 2) * start.y - Math.pow(t, 2) * end.y) / (2 * (1 - t) * t);
    return { x: retX, y: retY };
}

function CBezierPath(p0: Point, p1: Point, p2: Point, p3: Point) {
    let path = `M ${p0.x} ${p0.y} `
    let t1 = (p1.x - p0.x) / (p3.x - p0.x)
    let t2 = (p2.x - p0.x) / (p3.x - p0.x)
    let [c1, c2] = getCControlPoints(p0, p1, p2, p3, t1, t2);
    path += ` C ${c1.x} ${c1.y} ${c2.x} ${c2.y} ${p3.x} ${p3.y}`

    return {
        path,
        c1,
        c2
    }
}

function SBezierPath(p0: Point, c1: Point, p2: Point, p3: Point) {
    let t = (p2.x - p0.x) / (p3.x - p0.x)
    let c2 = getSControlPoint(p0, c1, p2, p3, t)
    let path = ` S ${c2.x} ${c2.y} ${p3.x} ${p3.y}`
    return {
        path,
        c1,
        c2
    }
}

export function generateBezierPath(points: Point[]) {
    if (points.length === 0) {
        return '';
    }

    if (points.length === 1) {
        return `M${points[0].x} ${points[0].y}`;
    }

    if (points.length === 2) {
        return `M -10 ${points[0].y}  L ${points[0].x} ${points[0].y} L${points[1].x} ${points[1].y} L ${points[1].x + 1000000} ${points[1].y}`;
    }

    points = points.sort((a, b) => a.x - b.x); 

    let path = `M -10 ${points[0].y}  L ${points[0].x} ${points[0].y}`;
    let i = 0
    let c
    if (points.length >= 4) {
        let ret = CBezierPath(points[0], points[1], points[2], points[3])
        path += ret.path
        i = 3
        c = ret.c2
    } else if (points.length === 3) {
        // let t = (points[1].x - points[0].x) / (points[2].x - points[0].x)
        c = getQControlPoint(points[0], points[2], points[1], 0.5)
        path += `M ${points[0].x} ${points[0].y} Q ${c.x} ${c.y} ${points[2].x} ${points[2].y}`
        i = 2
    }

    for (; i < points.length - 2; i += 2) {
        let t = (points[i + 1].x - points[i].x) / (points[i + 2].x - points[i].x)
        let c1x = points[i].x + (points[i].x - c.x)
        let c1y = points[i].y + (points[i].y - c.y)
        let c1 = { x: c1x, y: c1y }
        let c2 = getSControlPoint(points[i], c1, points[i + 1], points[i + 2], t)
        path += ` C ${c1.x} ${c1.y} ${c2.x} ${c2.y} ${points[i + 2].x} ${points[i + 2].y}`
        c = c2
    }

    for (; i < points.length - 1; i += 1) {
        let c1x = points[i].x + (points[i].x - c.x)
        let c1y = points[i].y + (points[i].y - c.y)
        let c1 = { x: c1x, y: c1y }
        path += ` Q  ${c1.x} ${c1.y} ${points[i + 1].x} ${points[i + 1].y}`
        c = c1
    }

    path += `L ${points[points.length - 1].x + 1000000} ${points[points.length - 1].y}`

    return path;
}

function getMousePos(e) {
    var svg = e.target
    if (e.target.tagName.toLowerCase() !== 'svg') {
        svg = e.target.ownerSVGElement;
    }

    // 获取SVG视窗坐标 
    var pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    var svgP = pt.matrixTransform(svg.getScreenCTM().inverse());

    return {
        x: svgP.x,
        y: svgP.y
    };
}

interface CurveEditorProps {
    svgWidth?: number
    svgHeight?: number
    points: Point[]
    onChange: (points: Point[]) => void
}

function CurveEditor({
    svgWidth = 255,
    svgHeight = 255,
    points = [],
    onChange = (points) => { },
}: CurveEditorProps) {
    const pointMovingIndexRef = useRef(-1)
    const svgRef = useRef<SVGSVGElement>(null)
    const pointsRef = useRef(points)
    function setPoints(data: Point[]) {
        if (!svgRef.current) {
            return
        }
        const svg = svgRef.current
        pointsRef.current = data
        svg.innerHTML = ""

        const path = document.createElementNS(svg.namespaceURI, 'path')
        path.setAttribute('d', generateBezierPath(data))
        path.setAttribute('stroke', 'white')
        path.setAttribute('stroke-width', '5')
        path.addEventListener('click', (e) => {
            e.stopPropagation()
            handleAddPoint(e)
        })

        svg.appendChild(path)

        data.forEach((point, index) => {
            const circle = document.createElementNS(svg.namespaceURI, 'circle')
            circle.setAttribute('cx', `${point.x}`)
            circle.setAttribute('cy', `${point.y}`)
            circle.setAttribute('r', `8`)
            circle.setAttribute('fill', 'green')
            circle.addEventListener('mousedown', (e) => {
                pointMovingIndexRef.current = index;
                e.stopPropagation();
            })
            svg.appendChild(circle)
        })
    }
    useEffect(() => {
        // 初始化默认控制点
        if (points.length === 0) {
            onChange([{ x: 0, y: svgWidth }, { x: svgWidth, y: 0 }]);
        }
    }, [])


    // 拖拽处理
    function handleDrag(index, newPos) {
        const newPoints = [...points];
        newPoints[index] = newPos;
        setPoints(newPoints)
    }

    // 增加控制点
    function handleAddPoint(e) {
        const pos = getMousePos(e);
        const newPoints = [...points, pos];
        onChange(newPoints);
    }
    setPoints(points)
    return <div>
        <div>
            <button onClick={e => {
                onChange([{ x: 0, y: svgWidth }, { x: svgWidth, y: 0 }]);
            }}>重置</button>
        </div>
        <svg
            ref={svgRef}
            width={'100%'}
            style={{
                backgroundColor: 'black',
                overflow: 'hidden',
            }}
            onMouseDown={e => {
                e.stopPropagation()
            }}
            onMouseMove={e => {
                if (pointMovingIndexRef.current == -1) {
                    return
                }
                const pos = getMousePos(e);
                if (pos.x < 0) {
                    pos.x = 0
                }
                if (pos.x > svgWidth) {
                    pos.x = svgWidth
                }
                if (pos.y < 0) {
                    pos.x = 0
                }
                if (pos.y > svgWidth) {
                    pos.y = svgWidth
                }

                handleDrag(pointMovingIndexRef.current, pos)
            }}
            onMouseUp={e => {
                pointMovingIndexRef.current = -1
                onChange(pointsRef.current)
            }}
            viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        >
        </svg>
    </div>
}

export default CurveEditor;