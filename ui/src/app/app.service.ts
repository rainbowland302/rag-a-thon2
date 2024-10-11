import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";

@Injectable()
export class AppService {
    constructor(private http: HttpClient) {}

    prefix = '/api'

    retrieveAns(message: string) {
        return this.http.post(`${this.prefix}/search`, { message });
    }
}