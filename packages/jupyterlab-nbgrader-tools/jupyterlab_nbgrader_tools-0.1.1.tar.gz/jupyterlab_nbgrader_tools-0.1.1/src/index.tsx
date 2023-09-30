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
    // Idea from: https://discourse.jupyter.org/t/jupyterlab-4-iterating-over-all-cells-in-a-notebook/20033
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
                  if (cellList.get(i).metadata.hasOwnProperty('editable')){
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

export default extension;
