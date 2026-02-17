import { Component, EventEmitter, OnDestroy, OnInit, Output } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { FileUploadService } from 'src/app/core/services/file-upload.service';
import { finalize, flatMap, switchMap, tap } from 'rxjs/operators';
import { Observable, of, Subscription } from 'rxjs';

@Component({
  selector: 'app-img-uploader',
  templateUrl: './img-uploader.component.html',
  styleUrls: ['./img-uploader.component.css'],
})
export class ImgUploaderComponent implements OnInit {
  @Output() public word: EventEmitter<string> = new EventEmitter<string>();
  @Output() public isLoading: EventEmitter<boolean> = new EventEmitter<boolean>();

  public form: FormGroup = new FormGroup({});
  public imagePreview: string | ArrayBuffer | null = null;  //-jc preview buffer

  private poll$?: Observable<any>;

  constructor(
    private readonly fb: FormBuilder,
    private readonly fileUploadService: FileUploadService,
  ) {
  }

  public ngOnInit(): void {
    this.form = this.fb.group({
      fileSource: [null, Validators.required],
    });
  }

  public onFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const files: FileList | null = input.files;

  const file = files && files.length ? files[0] : null;

  // keep existing behaviour
  this.form.patchValue({ fileSource: file });

  //-jc add preview support
  if (!file) {
    this.imagePreview = null;
    return;
  }

  const reader = new FileReader();
  reader.onload = () => {
    this.imagePreview = reader.result;
  };
  reader.readAsDataURL(file);
}

  public uploadFile(): void {
    const { fileSource } = this.form.getRawValue();

    if (fileSource) {
      this.isLoading.emit(true);
      this.fileUploadService.uploadFile(fileSource)
        .pipe(
          switchMap(({id}) => this.fileUploadService.pollFileDataById(id)),
          finalize(() => this.isLoading.emit(false)),
        )
        .subscribe(word => this.word.emit(word?.text ?? word));
    }
  }
}
