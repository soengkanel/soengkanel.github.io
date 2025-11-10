package com.ng.service;

import com.ng.modal.Branch;
import com.ng.modal.Store;

/**
 * Service for initializing sample F&B data (menu items, tables, categories)
 * when a new F&B or HYBRID store is created
 */
public interface FnbInitializationService {

    /**
     * Initialize sample menu items, categories, and tables for a new F&B store
     *
     * @param store The newly created store
     * @param branch The main branch (if exists)
     */
    void initializeFnbSampleData(Store store, Branch branch);
}
