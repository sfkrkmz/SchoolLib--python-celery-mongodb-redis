Adımlar

NOT: Projenin çalışması için eksik modülleri  "pip install <modulename>" komutu ile indirebilirsiniz. 


1- powershell üzerinden dosya dizinine gidin ve " python.exe app.py " komutunu çalıştırın. 
2- "Redis" klasöründe "redis-server.exe" dosyasını çalıştırın. ( çift tık ) 
3- cmd üzerinden dosya dizinine gidin ve "celery -A app.celery worker --pool=solo -l info" komutunu çalıştırın.

proje ayağa kaldırıldı.

linkler

localhost:5001/register 	=> üye olma
localhost:5001/login  		=> login olma
localhost:5001/addbook		=> sisteme kitap ekleme
localhost:5001/searchbook	=> sistemdeki kitapları arama (küçük-büyük harf duyarlıdır Örnek arama: Kaşa )
localhost:5001/mybooks 		=> daha önce aldığınız üzerinize kayıtlı olan kitapları görebilir ve teslim edebilirsiniz ( with: Celery Task )


Arama yaptıktan sonra "localhost:5001/inlib" url sine yönlendirileceksiniz. Kütüphanede bulunan ve almak istediğiniz kitabı seçerek "Kitabı Al" butonuna basınız.
zorunlu alanları doldurup "Submit" butonu ile kitabı alabilirsiniz ( With: Celery Task )



-Servis ağırlıklı olarak form-data kabul etmektedir.
-Bazı metodlarda json-data kontrolü de yapılmıştır.

Projenin tüm metodlarının çalışmasını test etmek için Postman gibi uygulamalar üzerinden istek atarken form-data gönderilmelidir. 