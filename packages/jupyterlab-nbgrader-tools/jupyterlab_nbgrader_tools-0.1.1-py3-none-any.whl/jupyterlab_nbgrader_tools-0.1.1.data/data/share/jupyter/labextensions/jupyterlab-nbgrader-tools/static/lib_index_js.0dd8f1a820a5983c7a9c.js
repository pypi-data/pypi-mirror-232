"use strict";
(self["webpackChunkjupyterlab_nbgrader_tools"] = self["webpackChunkjupyterlab_nbgrader_tools"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);

const extension = {
    id: 'jupyterlab-nbgrader-tools:plugin',
    autoStart: true,
    requires: [_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILabShell],
    activate: (app) => {
        console.log('JupyterLab extension jupyterlab-nbgrader-tools is activated!');
        // Nbgrader graded cells highlight
        // Idea from: https://discourse.jupyter.org/t/jupyterlab-4-iterating-over-all-cells-in-a-notebook/20033
        const labShell = app.shell;
        labShell.currentChanged.connect(() => {
            const notebook = app.shell.currentWidget;
            if (notebook) {
                notebook.revealed.then(() => {
                    if (notebook.content.model) {
                        // console.log('NOTEBOOK content: ', notebook.content)
                        // console.log('NOTEBOOK widgets: ', notebook.content.widgets)
                        const cellList = notebook.content.model.cells;
                        const widgetList = notebook.content.widgets;
                        // Loop over all cells in the notebook
                        for (let i = 0; i < cellList.length; i++) {
                            // console.log('DATA: ', cellList.get(i))
                            // console.log('TYPE: ', cellList.get(i).type)
                            // console.log('METADATA: ', cellList.get(i).metadata)
                            // console.log('WIDGET: ', widgetList[i])
                            // Add class to code cells with nbgrader metadata
                            if (cellList.get(i).type == 'code' &&
                                cellList.get(i).metadata.hasOwnProperty('nbgrader')) {
                                widgetList[i].node.classList.add('gradedquestioncode');
                            }
                            // Add class to markdown cells with nbgrader metadata
                            if (cellList.get(i).type == 'markdown' &&
                                cellList.get(i).metadata.hasOwnProperty('nbgrader')) {
                                // Skip markdown cells with editable metadata (readonly cells)
                                if (cellList.get(i).metadata.hasOwnProperty('editable')) {
                                    continue;
                                }
                                widgetList[i].node.classList.add('gradedquestionmd');
                            }
                            // Add class to all cells with nbgrader metadata
                            if (cellList.get(i).metadata.hasOwnProperty('nbgrader')) {
                                widgetList[i].node.classList.add('gradedquestion');
                            }
                        }
                    }
                });
            }
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (extension);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.0dd8f1a820a5983c7a9c.js.map