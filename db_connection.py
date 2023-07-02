from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


class DbConnection:
    """ПОКА НЕ ИСПОЛЬЗУЕТСЯ"""
    # TODO - Протестировать этот класс взамен использования глобальных переменных `_client`, `_db`, `_collection`

    def __init__(self, client_uri: str, db_name: str, collection_name: str):
        self.client_uri = client_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self._client: AsyncIOMotorClient = None
        self._db: AsyncIOMotorDatabase = None
        self._collection: AsyncIOMotorCollection = None

    def __call__(self) -> None:
        self._client, self._db, self._collection = self.get_client_connection(self.client_uri,
                                                                              self.db_name,
                                                                              self.collection_name)

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db

    @property
    def collection(self):
        return self._collection

    def get_client_connection(self, client_uri: str = None, db_name: str = None,
                              collection_name: str = None) -> tuple[AsyncIOMotorClient,
                                                                    AsyncIOMotorDatabase,
                                                                    AsyncIOMotorCollection]:
        """
        Создаем подключение к Базе данных. Если параметры не заданы - значит заполняем поля самого объекта.
        :param client_uri:
        :param db_name:
        :param collection_name:
        :return:
        """
        if client_uri:
            client = AsyncIOMotorClient(client_uri)
            db = client[db_name]
            collection = db[collection_name]
        else:
            if self._client is None:     # Создаем подключение, если оно еще не было задано
                self._client = AsyncIOMotorClient(client_uri)

            if db_name:     # Если передано новое имя БД - используем его.
                self._db = self._client[db_name]
            else:
                self._db = self._client[self.db_name]

            if collection_name:     # Если передано новое имя Коллекции - используем его.
                self._collection = self._db[collection_name]
            else:
                self._collection = self._db[self.collection_name]

            client = self._client
            db = self._db
            collection = self._collection

        print('Server connection was opened')
        return client, db, collection

    def disconnect_from_client(self, client: AsyncIOMotorClient = None) -> None:
        if client is not None:              # Если клиент передан в параметре - закрываем его
            client.close()
            print('Server connection was closed')
        elif self._client is not None:       # Если клиент не передан, но существует открытое соединение - закрываем его
            self._client.close()
            print('Server connection was closed')
        else:
            print('Connection not set')
