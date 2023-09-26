"use strict";
(self["webpackChunkgrist_widget"] = self["webpackChunkgrist_widget"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var comlink__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! comlink */ "webpack/sharing/consume/default/comlink/comlink");
/* harmony import */ var comlink__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(comlink__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _initKernelPy__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./initKernelPy */ "./lib/initKernelPy.js");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1__);



const pendingWorkers = [];
class MyWorker extends Worker {
    constructor(scriptURL, options) {
        super(scriptURL, options);
        const { grist } = window;
        if (grist) {
            exposeWorker(this, grist);
        }
        else {
            pendingWorkers.push(this);
        }
    }
}
window.Worker = MyWorker;
const emptyNotebook = {
    content: {
        'metadata': {
            'language_info': {
                'codemirror_mode': {
                    'name': 'python',
                    'version': 3
                },
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.11'
            },
            'kernelspec': {
                'name': 'python',
                'display_name': 'Python (Pyodide)',
                'language': 'python'
            }
        },
        'nbformat_minor': 4,
        'nbformat': 4,
        'cells': [
            {
                'cell_type': 'code',
                'source': '',
                'metadata': {},
                'execution_count': null,
                'outputs': []
            }
        ]
    },
    format: 'json',
};
let currentRecord = null;
/**
 * Initialization data for the grist-widget extension.
 */
const plugin = {
    id: 'grist-widget:plugin',
    description: 'Custom Grist widget for a JupyterLite notebook',
    autoStart: true,
    requires: [_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1__.IFileBrowserCommands],
    activate: (app) => {
        hideBars(app).catch(e => console.error(e));
        const script = document.createElement('script');
        script.src = 'https://docs.getgrist.com/grist-plugin-api.js';
        script.id = 'grist-plugin-api';
        script.addEventListener('load', async () => {
            const grist = window.grist;
            app.serviceManager.contents.fileChanged.connect(async (_, change) => {
                var _a;
                if (change.type === 'save' && ((_a = change.newValue) === null || _a === void 0 ? void 0 : _a.path) === 'notebook.ipynb') {
                    grist.setOption('notebook', change.newValue);
                }
            });
            grist.onRecord((record) => {
                currentRecord = record;
            });
            grist.ready();
            const notebook = await grist.getOption('notebook') || emptyNotebook;
            await app.serviceManager.contents.save('notebook.ipynb', notebook);
            await app.commands.execute('filebrowser:open-path', { path: 'notebook.ipynb' });
            console.log('JupyterLab extension grist-widget is activated!');
            const kernel = await getKernel(app);
            kernel.requestExecute({ code: _initKernelPy__WEBPACK_IMPORTED_MODULE_2__["default"] });
            for (const worker of pendingWorkers) {
                exposeWorker(worker, grist);
            }
            await app.commands.execute('notebook:run-all-cells');
        });
        document.head.appendChild(script);
    }
};
async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
function exposeWorker(worker, grist) {
    comlink__WEBPACK_IMPORTED_MODULE_0__.expose({
        grist: {
            ...grist,
            getTable: (tableId) => comlink__WEBPACK_IMPORTED_MODULE_0__.proxy(grist.getTable(tableId)),
            getCurrentRecord: () => currentRecord,
        }
    }, worker);
}
async function getKernel(app) {
    var _a, _b, _c;
    while (true) {
        app.serviceManager.sessions.ready;
        const widget = app.shell.currentWidget;
        const kernel = (_c = (_b = (_a = widget === null || widget === void 0 ? void 0 : widget.context) === null || _a === void 0 ? void 0 : _a.sessionContext) === null || _b === void 0 ? void 0 : _b.session) === null || _c === void 0 ? void 0 : _c.kernel;
        if (kernel) {
            return kernel;
        }
        await delay(100);
    }
}
async function hideBars(app) {
    while (!app.shell.currentWidget) {
        await delay(100);
    }
    const shell = app.shell;
    shell.collapseLeft();
    shell._titleHandler.parent.setHidden(true);
    shell._leftHandler.sideBar.setHidden(true);
    for (let i = 0; i < 1000; i++) {
        if (!shell.leftCollapsed) {
            shell.collapseLeft();
            shell._leftHandler.sideBar.setHidden(true);
            break;
        }
        else {
            await delay(10);
        }
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/initKernelPy.js":
/*!*****************************!*\
  !*** ./lib/initKernelPy.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
// language=Python
const code = `
def __make_grist_api():
    from pyodide.ffi import to_js, create_proxy
    import js
    import pyodide_js
    import inspect
    import traceback
    import asyncio
    
    async def maybe_await(value):
        while inspect.isawaitable(value):
            value = await value
        return value
    
    def run_async(coro):
        if inspect.iscoroutinefunction(coro):
            coro = coro()
        asyncio.get_running_loop().run_until_complete(coro)

    class ComlinkProxy:
        def __init__(self, proxy, name=None):
            self._proxy = proxy
            self._name = name

        def __getattr__(self, name):
            return ComlinkProxy(getattr(self._proxy, name), name)

        async def __call__(self, *args, **kwargs):
            if any(callable(arg) for arg in args):
                assert len(args) == 1 and not kwargs, "Only one argument is supported for callbacks"
                [callback] = args
                async def wrapper(*callback_args):
                    callback_args = [
                        a.to_py() if hasattr(a, "to_py") else a
                        for a in callback_args
                    ]
                    await maybe_await(callback(*callback_args))

                js._grist_tmp1 = self._proxy
                js._grist_tmp2 = js.Comlink.proxy(create_proxy(wrapper))
                result = await js.eval("_grist_tmp1(_grist_tmp2)")
            else:
                args = [
                    to_js(arg, dict_converter=js.Object.fromEntries)
                    for arg in args
                ]
                kwargs = {
                    key: to_js(value, dict_converter=js.Object.fromEntries)
                    for key, value in kwargs.items()
                }
                result = await self._proxy(*args, **kwargs)

            if self._name == "getTable":
                result = ComlinkProxy(result)
            elif hasattr(result, "to_py"):
                result = result.to_py()
            return result

    js.importScripts("https://unpkg.com/comlink@4.4.1/dist/umd/comlink.js")
    pyodide_js.registerComlink(js.Comlink)
    
    get_ipython().display_formatter.formatters['text/plain'].for_type(
        str, lambda string, pp, cycle: pp.text(string)
    )
    
    def auto_display():
        handles = [display(display_id=True) for _ in range(45)]
        
        def start():
            for handle in handles:
                handle.update({}, raw=True)

            i = 0
            def disp(obj):
                nonlocal i
                if i == len(handles) - 1:
                    handles[i].update("Too many display calls!")
                else:
                    handles[i].update(obj)
                    i += 1
            return disp
        return start
    
    def wrap_with_display(wrapper):
        disp_start = auto_display()
        async def inner_wrapper(*args):
            displayer = disp_start()
            try:
                await maybe_await(wrapper(displayer, *args))
            except Exception as e:
                displayer("".join(traceback.format_exception(
                    e.__class__, e, skip_traceback_internals(e.__traceback__)
                )))
                
        return inner_wrapper

    def skip_traceback_internals(tb):
        filename = (lambda: 0).__code__.co_filename
        original = tb
        while tb and tb.tb_frame.f_code.co_filename == filename:
            tb = tb.tb_next
        if tb:
            return tb
        else:
            return original

    class Grist:
        def __init__(self):
            self.raw = ComlinkProxy(js.Comlink.wrap(js).grist)
        
        def on_records(self, callback):
            @wrap_with_display
            async def wrapper(displayer, _, *rest):
                records = await self.raw.fetchSelectedTable(keepEncoded=True)
                return callback(displayer, records, *rest)

            @run_async
            async def run():
                await wrapper(None)
                await self.raw.onRecords(wrapper)
    
        def on_record(self, callback):
            @wrap_with_display
            async def wrapper(displayer, record, *rest):
                if record:
                    record = await self.raw.fetchSelectedRecord(record['id'], keepEncoded=True)
                    return callback(displayer, record, *rest)
            
            @run_async
            async def run():
                await wrapper(await self.raw.getCurrentRecord())
                await self.raw.onRecord(wrapper)
    
    
    return Grist() 


grist = __make_grist_api()
`;
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (code);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.18f5340ed4130e7d36b1.js.map