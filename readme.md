# Dokumentacja Docker dla projektu wypożyczalni samochodów

## Spis treści
1. [Wprowadzenie](#wprowadzenie)
2. [Analiza Dockerfile](#analiza-dockerfile)
3. [Najlepsze praktyki](#najlepsze-praktyki)
4. [Konfiguracja Docker Compose](#konfiguracja-docker-compose)
5. [Rekomendacje dotyczące analizy podatności](#rekomendacje-dotyczące-analizy-podatności)
6. [Wytyczne Docker Scout / Trivy](#wytyczne-docker-scout--trivy)
7. [Opis manifestow K8S](#opis-manifestow-k8s)

---

## Wprowadzenie
Ten dokument zawiera kompleksowe wskazówki dotyczące korzystania z Dockera w projekcie wypożyczalni samochodów. Obejmuje analizę Dockerfile, najlepsze praktyki, konfiguracje Docker Compose oraz rekomendacje dotyczące zarządzania podatnościami.

## Analiza Dockerfile
- **Struktura**: Dockerfile powinien jasno definiować obraz bazowy oraz odpowiedzialność poszczególnych warstw.
- **Budowanie wieloetapowe (Multi-Stage Builds)**: Używaj budowania wieloetapowego w celu efektywnego tworzenia obrazów i minimalizacji ich końcowego rozmiaru.
- **Cache warstw**: Uporządkuj instrukcje według częstotliwości zmian, aby maksymalnie wykorzystać cache i skrócić czas budowania.

## Najlepsze praktyki
- **Minimalizacja rozmiaru obrazu**: Używaj lekkich obrazów bazowych (np. alpine), gdy tylko jest to możliwe.
- **Określanie wersji**: Zawsze określaj wersje obrazów bazowych i zależności, aby zapewnić spójność.
- **Bezpieczeństwo**: Uruchamiaj kontenery jako użytkownik inny niż root, unikaj przechowywania wrażliwych informacji w obrazach oraz regularnie aktualizuj obrazy.

## Konfiguracja Docker Compose
- **Definicja usług**: Jasno definiuj usługi z odpowiednimi ustawieniami sieci, wolumenów i zmiennych środowiskowych.
- **Healthchecki**: Wdrażaj mechanizmy sprawdzania stanu usług, aby zapewnić ich poprawne działanie i automatyczne restartowanie w razie awarii.
- **Zarządzanie wolumenami**: Używaj nazwanych wolumenów do przechowywania danych trwałych oraz bind mountów w środowisku deweloperskim.

### Przykładowy docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    image: car_rental_app:latest
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - data:/var/lib/data

volumes:
  data:
```
## Rekomendacje dotyczące analizy podatności
- **Regularne skanowanie**: Korzystaj z narzędzi takich jak Trivy lub Snyk, aby regularnie skanować obrazy i zależności pod kątem podatności.
- **Aktualizacja zależności**: Utrzymuj wszystkie zależności oraz obrazy bazowe Dockera na bieżąco, aby ograniczyć ryzyko podatności.

## Wytyczne Docker Scout / Trivy
- **Instalacja**: Trivy można łatwo zainstalować za pomocą Homebrew lub jako kontener Docker.
- **Polecenie skanowania**: Użyj komendy `trivy image <twoja_nazwa_obrazu>`, aby przeskanować obraz pod kątem podatności.
- **Interpretacja wyników**: Dokładnie analizuj wyniki skanowania, koncentrując się na krytycznych podatnościach i zalecanych poprawkach.

## Opis manifestow K8S
**1. Przestrzeń nazw (Namespace)**
Cały system jest wdrażany w dedykowanej przestrzeni nazw o nazwie car-rental-ns.
Użycie dedykowanego namespace'a pozwala na logiczne odseparowanie zasobów projektu od innych aplikacji działających w klastrze, ułatwia zarządzanie uprawnieniami (RBAC) oraz ułatwia sprzątanie środowiska.

**2. Obiekty wdrażania (Deployment / StatefulSet)**
System wykorzystuje dwa główne typy obiektów do zarządzania pracą kontenerów, dobrane odpowiednio do charakteru poszczególnych mikrousług:
Deployment (Aplikacje bezstanowe)
Mikroserwisy frontend, car-service oraz rental-service są aplikacjami bezstanowymi (stateless), dlatego użyto dla nich obiektu typu Deployment.
Dla każdego z tych serwisów zdefiniowano replicas: 2. Dwie repliki zapewniają wysoką dostępność (High Availability) oraz umożliwiają zrównoważenie obciążenia ruchem przychodzącym.
W przypadku car-service zastosowano dodatkowo mechanizm podAntiAffinity, który preferuje uruchamianie podów na różnych węzłach klastra (topologyKey: "kubernetes.io/hostname"), co dodatkowo zwiększa odporność na awarię pojedynczego węzła.
StatefulSet (Baza danych)
Dla bazy danych MongoDB wybrano obiekt typu StatefulSet z liczbą replik ustawioną na 1 (replicas: 1).
Wybór ten jest podyktowany faktem, że baza danych jest aplikacją stanową. StatefulSet gwarantuje stabilny identyfikator sieciowy oraz bezpieczne podpinanie wolumenów z danymi, co jest kluczowe dla zachowania spójności bazy w przypadku restartu poda.

**3. Usługi sieciowe (Services)**
Wszystkie usługi w klastrze (car-service-service, rental-service-service, frontend-service, mongodb-service) zostały skonfigurowane jako typ ClusterIP.
Typ ClusterIP wystawia usługę na wewnętrznym adresie IP klastra, co oznacza, że serwisy te są dostępne tylko z poziomu innych aplikacji wewnątrz klastra (np. car-service i rental-service komunikujące się z mongodb-service na porcie 27017). Jest to optymalne z punktu widzenia bezpieczeństwa - nie wystawiamy bezpośrednio portów poszczególnych mikrousług na zewnątrz klastra. Dostęp zewnętrzny realizowany jest centralnie za pomocą Ingressa.

**4. Dostęp z zewnątrz (Ingress)**
Do obsługi ruchu z zewnątrz klastra wybrano rozwiązanie Ingress wykorzystujące klasę nginx (ingressClassName: nginx).
Ruch kierowany jest na host car-rental.local.
Uzasadnienie i konfiguracja: Wybór Ingressa zamiast wielu usług typu LoadBalancer pozwala na oszczędność zasobów i ujednolicenie punktu wejścia do aplikacji. Ingress realizuje routing oparty na ścieżkach:
Ruch na ścieżkę /api/cars/?(.*) jest przekierowywany do usługi car-service-service na port 8000.
Ruch na ścieżkę /api/rentals/?(.*) trafia do rental-service-service na port 8000.
Pozostały ruch (ścieżka /(.*)) obsługiwany jest przez frontend-service na porcie 80.
Użyto adnotacji nginx.ingress.kubernetes.io/rewrite-target: /$1, która ułatwia dynamiczne przepisywanie ścieżek URL trafiających do backendowych mikrousług.

**5. Przechowywanie danych (PV / PVC / StorageClass)**
Mechanizm trwałego przechowywania danych został zrealizowany dla bazy danych MongoDB przy użyciu PersistentVolumeClaim (PVC) o nazwie mongodb-pvc.
Zgłoszenie PVC żąda 2Gi przestrzeni dyskowej z domyślnej klasy pamięci standard z prawami dostępu ReadWriteOnce.
Utworzony wolumen (pod nazwą mongo-storage) jest następnie montowany wewnątrz kontenera MongoDB w ścieżce /data/db. Dzięki temu dane zapisane w bazie przetrwają cykl życia pojedynczego poda.

**6. Wstrzykiwanie konfiguracji (ConfigMap / Secrets)**
Konfiguracja aplikacji jest odseparowana od obrazów kontenerów, co ułatwia migrację między środowiskami. Wdrożenie wykorzystuje zarówno ConfigMap, jak i Secret.
ConfigMap (rental-config): Przechowuje jawne parametry konfiguracyjne, takie jak adres połączenia do bazy danych: MONGO_URL: "mongodb://mongodb-service:27017". Wartość ta jest wstrzykiwana jako zmienna środowiskowa MONGO_URL do kontenerów car-service oraz rental-service z użyciem valueFrom.configMapKeyRef.
Secret (rental-secret): Przechowuje wrażliwe dane, w tym przypadku klucz aplikacji APP_SECRET_KEY, który został zakodowany w formacie Base64. Użycie typu Opaque gwarantuje, że dane wrażliwe nie są przechowywane otwartym tekstem bezpośrednio w repozytorium czy zmiennych bezstanowych.
