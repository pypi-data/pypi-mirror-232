/*! For license information please see 3585.225d1e4e8e91981f6e1f.js.LICENSE.txt */
"use strict";(self.webpackChunkjupyterlab_nodeeditor=self.webpackChunkjupyterlab_nodeeditor||[]).push([[3585],{3585:(e,n,t)=>{t.r(n),t.d(n,{conf:()=>s,language:()=>d});var r=t(797),o=Object.defineProperty,l=Object.getOwnPropertyDescriptor,a=Object.getOwnPropertyNames,i=Object.prototype.hasOwnProperty,c=(e,n,t,r)=>{if(n&&"object"==typeof n||"function"==typeof n)for(let c of a(n))i.call(e,c)||c===t||o(e,c,{get:()=>n[c],enumerable:!(r=l(n,c))||r.enumerable});return e},u={};c(u,r,"default");var s={comments:{lineComment:"#"},brackets:[["{","}"],["[","]"],["(",")"]],autoClosingPairs:[{open:"{",close:"}"},{open:"[",close:"]"},{open:"(",close:")"},{open:'"',close:'"'},{open:"'",close:"'"}],surroundingPairs:[{open:"{",close:"}"},{open:"[",close:"]"},{open:"(",close:")"},{open:'"',close:'"'},{open:"'",close:"'"}],folding:{offSide:!0},onEnterRules:[{beforeText:/:\s*$/,action:{indentAction:u.languages.IndentAction.Indent}}]},d={tokenPostfix:".yaml",brackets:[{token:"delimiter.bracket",open:"{",close:"}"},{token:"delimiter.square",open:"[",close:"]"}],keywords:["true","True","TRUE","false","False","FALSE","null","Null","Null","~"],numberInteger:/(?:0|[+-]?[0-9]+)/,numberFloat:/(?:0|[+-]?[0-9]+)(?:\.[0-9]+)?(?:e[-+][1-9][0-9]*)?/,numberOctal:/0o[0-7]+/,numberHex:/0x[0-9a-fA-F]+/,numberInfinity:/[+-]?\.(?:inf|Inf|INF)/,numberNaN:/\.(?:nan|Nan|NAN)/,numberDate:/\d{4}-\d\d-\d\d([Tt ]\d\d:\d\d:\d\d(\.\d+)?(( ?[+-]\d\d?(:\d\d)?)|Z)?)?/,escapes:/\\(?:[btnfr\\"']|[0-7][0-7]?|[0-3][0-7]{2})/,tokenizer:{root:[{include:"@whitespace"},{include:"@comment"},[/%[^ ]+.*$/,"meta.directive"],[/---/,"operators.directivesEnd"],[/\.{3}/,"operators.documentEnd"],[/[-?:](?= )/,"operators"],{include:"@anchor"},{include:"@tagHandle"},{include:"@flowCollections"},{include:"@blockStyle"},[/@numberInteger(?![ \t]*\S+)/,"number"],[/@numberFloat(?![ \t]*\S+)/,"number.float"],[/@numberOctal(?![ \t]*\S+)/,"number.octal"],[/@numberHex(?![ \t]*\S+)/,"number.hex"],[/@numberInfinity(?![ \t]*\S+)/,"number.infinity"],[/@numberNaN(?![ \t]*\S+)/,"number.nan"],[/@numberDate(?![ \t]*\S+)/,"number.date"],[/(".*?"|'.*?'|[^#'"]*?)([ \t]*)(:)( |$)/,["type","white","operators","white"]],{include:"@flowScalars"},[/.+?(?=(\s+#|$))/,{cases:{"@keywords":"keyword","@default":"string"}}]],object:[{include:"@whitespace"},{include:"@comment"},[/\}/,"@brackets","@pop"],[/,/,"delimiter.comma"],[/:(?= )/,"operators"],[/(?:".*?"|'.*?'|[^,\{\[]+?)(?=: )/,"type"],{include:"@flowCollections"},{include:"@flowScalars"},{include:"@tagHandle"},{include:"@anchor"},{include:"@flowNumber"},[/[^\},]+/,{cases:{"@keywords":"keyword","@default":"string"}}]],array:[{include:"@whitespace"},{include:"@comment"},[/\]/,"@brackets","@pop"],[/,/,"delimiter.comma"],{include:"@flowCollections"},{include:"@flowScalars"},{include:"@tagHandle"},{include:"@anchor"},{include:"@flowNumber"},[/[^\],]+/,{cases:{"@keywords":"keyword","@default":"string"}}]],multiString:[[/^( +).+$/,"string","@multiStringContinued.$1"]],multiStringContinued:[[/^( *).+$/,{cases:{"$1==$S2":"string","@default":{token:"@rematch",next:"@popall"}}}]],whitespace:[[/[ \t\r\n]+/,"white"]],comment:[[/#.*$/,"comment"]],flowCollections:[[/\[/,"@brackets","@array"],[/\{/,"@brackets","@object"]],flowScalars:[[/"([^"\\]|\\.)*$/,"string.invalid"],[/'([^'\\]|\\.)*$/,"string.invalid"],[/'[^']*'/,"string"],[/"/,"string","@doubleQuotedString"]],doubleQuotedString:[[/[^\\"]+/,"string"],[/@escapes/,"string.escape"],[/\\./,"string.escape.invalid"],[/"/,"string","@pop"]],blockStyle:[[/[>|][0-9]*[+-]?$/,"operators","@multiString"]],flowNumber:[[/@numberInteger(?=[ \t]*[,\]\}])/,"number"],[/@numberFloat(?=[ \t]*[,\]\}])/,"number.float"],[/@numberOctal(?=[ \t]*[,\]\}])/,"number.octal"],[/@numberHex(?=[ \t]*[,\]\}])/,"number.hex"],[/@numberInfinity(?=[ \t]*[,\]\}])/,"number.infinity"],[/@numberNaN(?=[ \t]*[,\]\}])/,"number.nan"],[/@numberDate(?=[ \t]*[,\]\}])/,"number.date"]],tagHandle:[[/\![^ ]*/,"tag"]],anchor:[[/[&*][^ ]+/,"namespace"]]}}}}]);