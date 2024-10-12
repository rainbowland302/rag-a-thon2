import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from "@angular/forms";
import { ClarityModule } from "@clr/angular";
import { CommonModule } from '@angular/common';

import { AppService } from "./app.service";

interface QueryResponse {
  question: string;
  answer: string;
  timestamp: Date;
}

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
    responses: QueryResponse[] = [];
    isLoading = false;

    search() {
        if (!this.message.trim()) return;
        
        this.isLoading = true;
        const question = this.message;
        this.service.retrieveAns(this.message).subscribe({
            next: (res: any) => {
                this.responses.unshift({
                    question: question,
                    answer: res.res,
                    timestamp: new Date()
                });
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
