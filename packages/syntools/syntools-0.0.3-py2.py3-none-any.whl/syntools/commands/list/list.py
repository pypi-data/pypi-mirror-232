import os
from ...core import Utils, Logging
import synapseclient as syn
import asyncio
from synapsis import Synapsis


class List:
    def __init__(self, synapse_id, recursive=True, count_only=False):
        self.start_id = synapse_id
        self.recursive = recursive
        self.count_only = count_only
        self.start_container = None
        self.queue = None
        self.result = None

    async def execute(self):
        Logging.print_log_file_path()
        self.result = ListResult(self.start_id)
        try:
            self.start_container = await Synapsis.Chain.get(self.start_id, downloadFile=False)

            if type(self.start_container) not in [syn.Project, syn.Folder]:
                self.result.errors.append('synapse-id must be a Synapse Project or Folder.')
                return self.result

            Logging.info('Listing: {0} ({1})'.format(self.start_container.name, self.start_container.id), console=True)

            self.queue = asyncio.Queue()
            producers = [asyncio.create_task(self._list(self.start_container, [self.start_container.name]))]
            worker_count = 5 if self.count_only else 1
            worker_count = int(os.environ.get('SYNTOOLS_LIST_WORKERS', worker_count))
            workers = [asyncio.create_task(self._worker()) for _ in range(worker_count)]
            await asyncio.gather(*producers)
            await self.queue.join()
            for worker in workers:
                worker.cancel()

        except Exception as ex:
            self.result.errors.append(str(ex))

        if self.count_only:
            Utils.print_inplace_reset()

        if self.result.errors:
            Logging.error('Finished with errors:', console=True)
            for error in self.result.errors:
                Logging.error(' - {0}'.format(error), console=True)
        else:
            folder_count = sum(i.type == 'Folder' for i in self.result.items)
            file_count = sum(i.type == 'File' for i in self.result.items)
            Logging.info('Total Items: {0}'.format(len(self.result.items)), console=True)
            Logging.info('Folders: {0}'.format(folder_count), console=True)
            Logging.info('Files: {0}'.format(file_count), console=True)
            Logging.info('Finished successfully.', console=True)

        return self.result

    async def _worker(self):
        while True:
            folder, paths = await self.queue.get()
            try:
                await self._list(folder.id, paths)
            except Exception as ex:
                self.result.errors.append(str(ex))

            self.queue.task_done()

    async def _list(self, parent, paths):
        try:
            folders = []
            async for child in Synapsis.Chain.getChildren(parent, includeTypes=["folder", "file"]):
                is_file = Synapsis.ConcreteTypes.get(child).is_file
                path = '/'.join(paths + [child['name']])
                synapse_item = ListResult.SynapseItem(child['id'], 'File' if is_file else 'Folder', child['name'], path)
                if is_file or not self.recursive:
                    self.result.items.append(synapse_item)
                    if self.count_only:
                        if len(self.result.items) % 100 == 0:
                            Utils.print_inplace('Counted {0} items...'.format(len(self.result.items)))
                    else:
                        Logging.info(' - [{0} - {1}] {2}'.format(synapse_item.type, synapse_item.id, synapse_item.path),
                                     console=True)
                else:
                    folders.append(synapse_item)

            for synapse_item in folders:
                self.result.items.append(synapse_item)
                if self.count_only:
                    if len(self.result.items) % 100 == 0:
                        Utils.print_inplace('Counted {0} items...'.format(len(self.result.items)))
                else:
                    Logging.info(' - [{0} - {1}] {2}'.format(synapse_item.type, synapse_item.id, synapse_item.path),
                                 console=True)
                await self.queue.put([synapse_item, paths + [synapse_item.name]])
        except Exception as ex:
            self.result.errors.append('Error listing: {0} - {1}'.format(parent, ex))


class ListResult:
    def __init__(self, synapse_id):
        self.synapse_id = synapse_id
        self.items = []
        self.errors = []

    class SynapseItem:
        def __init__(self, id, type, name, path):
            self.id = id
            self.type = type
            self.name = name
            self.path = path
