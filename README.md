 [programmer : ekoabdulaziz96@gmail.com]

informasi : 
 1. file routing user           : resources/users.py
 2. file routing transaction    : resources/transactions.py
 3. routing/path endpoint api dibuat berdasarkan dokumentasi file PDF test tahap 2
 4. semua endpoint sudah berhasil dibuat
 5. contoh data input user      : example_data_users.json
 6. contoh data input transaction: example_data_transactions.json
 7. mongoDB saat development dijalankan menggunakan docker 
 8. belum terdapat unit test
 9. untuk backgroud process dan antrian belum berhasil diimplementasikan, pengalaman author tentang penggunaan celery perlu ditambah lagi
 10. pemakaian fitur transaction pada mongoDB belum bisa diimplementasikan sebagai gantinya dibuat design pattern Rollback transaction


Run Program : 
1. pastikan python sudah terisntall dan buka cmd/powershell di tepat diluar folder bismillah_keda
2. siapkan virtualenvironment baru dan aktifkan. (tidak wajib)
   NB : untuk windows
    - pip install virtualenv
    - virtualenv venv
    - ./venv/script/activate  (powershell)
4. masuk ke folder program 
    - cd bismillahSpin
3. install requirements program
    - pip install -r requirements.txt
4. persiapan sebelum running
    a. mongoDB
        - disarankan menggunakan docker dan docker-compose.yml di folder ini
        - run mongoDB :
            - pastikan tidak ada server mongoDB yang sedang hidup, krn dikhawatirkan akan terjadi konflik
            - pastikan docker sudah berjalan
            - eksekusi perintash berikut [tanpa tanda petik dua] 
                "docker-compose -f docker-compose.yml up -d" , [-d opsional, agar proses berjalan di backgroud]
            - tunggu sampai build image dan container selesai
            - buka link "http://localhost:8081/" di browser,
            -  masukkan username: admin pass: admin123 [bila gagal coba username: root pass: pass12345]
        - bila menggunakan mongoDB sendiri, maka ada setting tambahan pada file settings.py pada variabel uri
            patterd: "mongodb://[user]:[password]@[host]:[port]/?authSource=admin"
            contoh : "mongodb://root:pass12345@localhost:27017/?authSource=admin"
            [sumber: https://pymongo.readthedocs.io/en/stable/examples/authentication.html]

5. jalankan program
    - python apps.py
6. bila berhasil maka akan berjasan di localhost pada port 5000  [localhost:5000]
7. untuk selanjutnya buka file PDF, untuk mengetahui endpoint API [Option] yang dibut.

struktur folder:
-bismillahSpin
-venv

NB:
- github public : https://github.com/ekoabdulaziz96/bismillah_kedaTech