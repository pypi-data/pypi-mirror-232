import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { ILauncher } from '@jupyterlab/launcher';
import { imageIcon } from '@jupyterlab/ui-components';

import { requestAPI } from './handler';

/**
 * Initialization data for the astronbs extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'astronbs:plugin',
  autoStart: true,
  optional: [
    ISettingRegistry,
    ILauncher,
    IFileBrowserFactory,
    IDocumentManager
  ],
  activate: (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null,
    launcher: ILauncher | null,
    fileBrowser: IFileBrowserFactory,
    docManager: IDocumentManager | null
  ) => {
    console.log('JupyterLab extension astronbs is activated!');

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('astronbs settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for astronbs.', reason);
        });
    }

    app.commands.addCommand('astronbs:reduction_template', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('reduction_template', {
          body: JSON.stringify({
            path: fileBrowser.defaultBrowser.model.path,
            package_path: 'astronbs.notebooks',
            nb_name: 'reduction_template.ipynb'
          }),
          method: 'POST'
        });
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: 'Reduction Template'
    });
    app.commands.addCommand('astronbs:reprojection_template', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('reprojection_template', {
          body: JSON.stringify({ path: fileBrowser.defaultBrowser.model.path }),
          method: 'POST'
        });
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: 'Reprojection Template'
    });

    app.commands.addCommand('astronbs:light_combo_template', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('light_combo_template', {
          body: JSON.stringify({ path: fileBrowser.defaultBrowser.model.path }),
          method: 'POST'
        });
        console.log('I am back in open2');
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: 'Light Combo Template'
    });

    app.commands.addCommand('astronbs:folder_viewer_template', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('folder_viewer_template', {
          body: JSON.stringify({ path: fileBrowser.defaultBrowser.model.path }),
          method: 'POST'
        });
        console.log('I am back in open15');
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: 'Folder Image Viewer'
    });

    app.commands.addCommand('astronbs:interactive_image_viewer', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('interactive_image_viewer', {
          body: JSON.stringify({ path: fileBrowser.defaultBrowser.model.path }),
          method: 'POST'
        });
        console.log('I am back in open11');
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: 'Interactive Image Viewer'
    });

    app.commands.addCommand('astronbs:quick_color_template', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('quick_color_template', {
          body: JSON.stringify({ path: fileBrowser.defaultBrowser.model.path }),
          method: 'POST'
        });
        console.log('I am back in open11');
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: 'Quick Color Image'
    });

    app.commands.addCommand('astronbs:color_mixer_template', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('color_mixer_template', {
          body: JSON.stringify({ path: fileBrowser.defaultBrowser.model.path }),
          method: 'POST'
        });
        console.log('I am back in open11');
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: 'Color Mixer'
    });

    app.commands.addCommand('astronbs:01_seeing_profile', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('nb_make', {
          body: JSON.stringify({
            path: fileBrowser.defaultBrowser.model.path,
            package_path: 'stellarphot.notebooks.photometry',
            nb_name: '01-viewer-seeing-template.ipynb'
          }),
          method: 'POST'
        });
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: '01 Seeing Profile'
    });

    app.commands.addCommand('astronbs:02_comp_stars', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('nb_make', {
          body: JSON.stringify({
            path: fileBrowser.defaultBrowser.model.path,
            package_path: 'stellarphot.notebooks.photometry',
            nb_name: '02-comp-star-plotter-template.ipynb'
          }),
          method: 'POST'
        });
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: '02 Comparison Stars'
    });

    app.commands.addCommand('astronbs:03_do_photometry', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('nb_make', {
          body: JSON.stringify({
            path: fileBrowser.defaultBrowser.model.path,
            package_path: 'stellarphot.notebooks.photometry',
            nb_name: '03-photometry-template.ipynb'
          }),
          method: 'POST'
        });
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: '03 Do photometry'
    });

    app.commands.addCommand('astronbs:transform_pared_back', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('nb_make', {
          body: JSON.stringify({
            path: fileBrowser.defaultBrowser.model.path,
            package_path: 'stellarphot.notebooks.photometry',
            nb_name: 'transform-pared-back.ipynb'
          }),
          method: 'POST'
        });
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: '04 Transform photometry'
    });

    app.commands.addCommand('astronbs:05_relative_flux', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('nb_make', {
          body: JSON.stringify({
            path: fileBrowser.defaultBrowser.model.path,
            package_path: 'stellarphot.notebooks.photometry',
            nb_name: '05-relative-flux-calculation-template.ipynb'
          }),
          method: 'POST'
        });
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: '05 Relative flux'
    });

    app.commands.addCommand('astronbs:06_transit_fitting', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('nb_make', {
          body: JSON.stringify({
            path: fileBrowser.defaultBrowser.model.path,
            package_path: 'stellarphot.notebooks.photometry',
            nb_name: '06-transit-fit-template.ipynb'
          }),
          method: 'POST'
        });
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: '06 Transit fitting'
    });

    app.commands.addCommand('astronbs:07_transit_fitting_exotic', {
      // code to run when this command is executed
      execute: () => {
        const reply = requestAPI<any>('nb_make', {
          body: JSON.stringify({
            path: fileBrowser.defaultBrowser.model.path,
            package_path: 'stellarphot.notebooks.photometry',
            nb_name: '07-transit-fit-with-exotic.ipynb'
          }),
          method: 'POST'
        });
        console.log(reply);
        reply.then(data => {
          console.log(data);
          if (docManager) {
            docManager.open(data['path']);
          }
        });
      },
      icon: imageIcon,
      label: '07 Transit fitting EXOTIC'
    });

    // Add item to launcher
    if (launcher) {
      launcher.add({
        command: 'astronbs:reduction_template',
        category: 'Astro',
        rank: 0
      });

      launcher.add({
        command: 'astronbs:reprojection_template',
        category: 'Astro',
        rank: 10
      });

      launcher.add({
        command: 'astronbs:light_combo_template',
        category: 'Astro',
        rank: 20
      });

      launcher.add({
        command: 'astronbs:folder_viewer_template',
        category: 'Astro',
        rank: 30
      });

      launcher.add({
        command: 'astronbs:interactive_image_viewer',
        category: 'Astro',
        rank: 40
      });

      launcher.add({
        command: 'astronbs:quick_color_template',
        category: 'Astro',
        rank: 50
      });

      launcher.add({
        command: 'astronbs:color_mixer_template',
        category: 'Astro',
        rank: 60
      });

      launcher.add({
        command: 'astronbs:01_seeing_profile',
        category: 'Photometry',
        rank: 0
      });
      launcher.add({
        command: 'astronbs:02_comp_stars',
        category: 'Photometry',
        rank: 0
      });
      launcher.add({
        command: 'astronbs:03_do_photometry',
        category: 'Photometry',
        rank: 0
      });
      launcher.add({
        command: 'astronbs:transform_pared_back',
        category: 'Photometry',
        rank: 0
      });
      launcher.add({
        command: 'astronbs:05_relative_flux',
        category: 'Photometry',
        rank: 0
      });
      launcher.add({
        command: 'astronbs:06_transit_fitting',
        category: 'Photometry',
        rank: 0
      });
      launcher.add({
        command: 'astronbs:07_transit_fitting_exotic',
        category: 'Photometry',
        rank: 0
      });
    }

    requestAPI<any>('get_example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The astronbs server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
