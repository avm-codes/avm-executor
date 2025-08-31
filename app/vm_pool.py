import os
import threading
import logging
from typing import List, Optional
from . import vm_library

logger = logging.getLogger(__name__)


class VMPool:
    """
    VM Pool that manages a pool of available VMs using vm_library
    """
    
    def __init__(self):
        self.pool_size = int(os.getenv('VM_POOL_SIZE', '3'))
        self.vm_pool: List[str] = []
        self.lock = threading.Lock()
        
        logger.info(f"Initializing VM Pool with size: {self.pool_size}")
        
        # Initialize pool at startup
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize pool using listActive and create additional VMs if needed"""
        try:
            active_vms_response = vm_library.list_active()
            logger.info(f"Found {len(active_vms_response)} active VMs from API")
            
            active_vm_ids = [vm["id"] for vm in active_vms_response]
            logger.info(f"Extracted VM IDs: {active_vm_ids}")
            
            with self.lock:
                # Add active VM IDs to pool
                self.vm_pool.extend(active_vm_ids)
                logger.info(f"Added {len(active_vm_ids)} VMs to pool: {active_vm_ids}")
                
                self._ensure_pool_size()
                
        except Exception as e:
            logger.error(f"Error initializing pool: {e}")
            with self.lock:
                self._ensure_pool_size()
    
    def _ensure_pool_size(self):
        """Ensure pool has the required number of VMs (must be called with lock held)"""
        current_size = len(self.vm_pool)
        needed = self.pool_size - current_size
        
        if needed > 0:
            logger.info(f"Pool has {current_size} VMs, need {needed} more to reach {self.pool_size}")
            
            for i in range(needed):
                try:
                    vm_id = vm_library.acquire()
                    self.vm_pool.append(vm_id)
                    logger.info(f"Created and added VM to pool: {vm_id}")
                except Exception as e:
                    logger.error(f"Failed to create VM for pool: {e}")
                    break
        else:
            logger.info(f"Pool is full with {current_size} VMs")
    
    def get_vm(self) -> Optional[str]:
        """
        Get a VM from pool and remove it from vm_pool.
        Then check if pool needs replenishment.
        """
        with self.lock:
            if not self.vm_pool:
                logger.warning("Pool is empty! Creating VM on demand")
                try:
                    vm_id = vm_library.acquire()
                    logger.info(f"Created VM on demand: {vm_id}")
                    return vm_id
                except Exception as e:
                    logger.error(f"Failed to create VM on demand: {e}")
                    return None
            
            vm_id = self.vm_pool.pop(0)
            logger.info(f"Got VM from pool: {vm_id}, pool size now: {len(self.vm_pool)}")
            
            self._ensure_pool_size()
            
            return vm_id
    
# Global pool instance
vm_pool = VMPool()

# Pool-based convenience functions
def get_vm_from_pool() -> Optional[str]:
    """Get a VM from the pool"""
    return vm_pool.get_vm()
