import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from "@angular/forms";
import { ClarityModule } from "@clr/angular";

import { AppService } from "./app.service";

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [RouterOutlet, ClarityModule, FormsModule],
    providers: [AppService],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent {
    constructor(
        private service: AppService,
    ) {

    }

    message = ""

    search() {
        this.service.retrieveAns(this.message).subscribe(res => {

        });
        this.message = "";
    }
}
