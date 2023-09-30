import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell,
  LabShell
} from '@jupyterlab/application';

import { NotebookPanel } from '@jupyterlab/notebook';

const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-nbgrader-tools:plugin',
  autoStart: true,
  requires: [ILabShell],
  activate: (
    app: JupyterFrontEnd,
  ) => {
    console.log('JupyterLab extension jupyterlab-nbgrader-tools is activated!');

    // Nbgrader graded cells highlight
    // Idea: https://discourse.jupyter.org/t/jupyterlab-4-iterating-over-all-cells-in-a-notebook/20033
    const labShell = app.shell as LabShell;
    labShell.currentChanged.connect(() => {
      const notebook = app.shell.currentWidget as unknown as NotebookPanel;
      if (notebook) {
          notebook.revealed.then(() => {
            if (notebook.content.model){
              // console.log('NOTEBOOK content: ', notebook.content)
              // console.log('NOTEBOOK widgets: ', notebook.content.widgets)
              const cellList = notebook.content.model.cells;
              const widgetList = notebook.content.widgets;
              for (let i = 0; i < cellList.length; i++) {
                // console.log('DATA: ', cellList.get(i))
                // console.log('TYPE: ', cellList.get(i).type)
                // console.log('METADATA: ', cellList.get(i).metadata)
                // console.log('widget: ', widgetList[i])
                if (cellList.get(i).type == 'code' && cellList.get(i).metadata.hasOwnProperty('nbgrader')) {
                  widgetList[i].node.classList.add('gradedquestioncode');
                }
                if (cellList.get(i).type == 'markdown' && cellList.get(i).metadata.hasOwnProperty('nbgrader')) {
                  widgetList[i].node.classList.add('gradedquestionmd');
                }
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

export default extension;
