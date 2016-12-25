import Inventory from './Inventory';
import InventoryStats from './InventoryStats';

Inventory.init();

const columnChart = document.getElementById('columnchart_values');
if (columnChart) {
  InventoryStats.init();
}
