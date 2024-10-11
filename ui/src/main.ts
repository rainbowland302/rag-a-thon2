import { bootstrapApplication } from '@angular/platform-browser';
import { ClarityIcons, searchIcon, circleArrowIcon } from "@cds/core/icon";

import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

ClarityIcons.addIcons(searchIcon, circleArrowIcon);

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
