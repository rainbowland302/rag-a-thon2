import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from "@angular/forms";
import { ClarityModule } from "@clr/angular";
import { CommonModule } from '@angular/common';

import { AppService } from "./app.service";

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [RouterOutlet, ClarityModule, FormsModule, CommonModule],
    providers: [AppService],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent {
    constructor(
        private service: AppService,
    ) {}

    message = "";
    response: string | null = null;
    isLoading = false;

    search() {
        this.isLoading = true;
        this.response = null;
        this.service.retrieveAns(this.message).subscribe({
            next: (res: any) => {
                this.response = res.res;
                this.isLoading = false;
            },
            error: (err) => {
                console.error('Error:', err);
                this.isLoading = false;
            }
        });
        this.message = "";
    }
}
