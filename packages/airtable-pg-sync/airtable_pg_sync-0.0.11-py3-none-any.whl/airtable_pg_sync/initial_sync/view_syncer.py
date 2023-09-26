import functools
import logging

from ..core.clients import postgres, airtable
from ..core.types import concepts, env_types


class ViewSyncer:

    def __init__(self, replication: env_types.Replication, specific_table: concepts.TableId = None):
        self.replication = replication
        self.specific_table = specific_table

    @functools.cached_property
    def logger(self) -> logging.Logger:
        return logging.getLogger('Schema Syncer')

    @functools.cache
    def _get_airtable_schema(self) -> list[concepts.Table]:
        self.logger.debug('Getting schema from Airtable')

        return airtable.Client(self.replication.base_id).get_schema()

    def _get_pg_schema(self) -> list[concepts.Table]:
        self.logger.debug('Getting schema from Postgres')

        return postgres.Client(self.replication.schema_name).get_schema()

    def drop_views(self):
        self.logger.info('Dropping views')

        for view in postgres.Client(self.replication.schema_name).get_all_views():

            if self.specific_table:
                corresponding_table = next((table for table in self._get_airtable_schema() if table.name == view), None)

                if not corresponding_table:
                    raise ValueError(f'Could not drop specific view because the name has changed')

                if corresponding_table.id != self.specific_table:
                    continue

            self.logger.info(f'Dropping view {view}')
            postgres.Client(self.replication.schema_name).drop_view(view_name=view)

    def create_views(self):
        self.logger.info('Creating views')
        pg_tables = {table.id: table for table in self._get_pg_schema()}

        for table in self._get_airtable_schema():

            if table.id not in pg_tables:
                continue

            if self.specific_table and table.id != self.specific_table:
                continue

            self.logger.info(f'Creating view {table.name}')

            db_table_fields = {field.id for field in pg_tables[table.id].fields}
            airtable_table_restricted_to_current_db_columns = concepts.Table(
                id=table.id,
                name=table.name,
                fields=[field for field in table.fields if field.id in db_table_fields],
            )

            postgres.Client(self.replication.schema_name).create_view(
                table=airtable_table_restricted_to_current_db_columns
            )

    def sync(self):
        self.logger.info('Syncing views')
        self.drop_views()
        self.create_views()
