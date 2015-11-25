'use strict';

WebMis20
.factory('PriceList', ['WMConfig', 'BasicModel', function (WMConfig, BasicModel) {
    var PriceList = function (data) {
        BasicModel.call(this, data);
    };
    PriceList.inheritsFrom(BasicModel);
    PriceList.initialize({
        fields: ['id', 'code', 'name', 'beg_date', 'end_date', 'finance', 'deleted'],
        base_url: WMConfig.url.misconfig.api_pricelist_base,
        list_url: WMConfig.url.misconfig.api_pricelist_list_base
    }, PriceList);
    return PriceList;
}])
.factory('PriceListItem', ['WMConfig', 'BasicModel', function (WMConfig, BasicModel) {
    var PriceListItem = function (data) {
        BasicModel.call(this, data);
    };
    PriceListItem.inheritsFrom(BasicModel);
    PriceListItem.initialize({
        fields: ['id', 'pricelist_id', 'beg_date', 'end_date', 'service_code', 'service_name',
            'deleted', 'price', 'service']
    }, PriceListItem);
    PriceListItem.getBaseUrl = function (args) {
        return WMConfig.url.misconfig.api_pricelist_item_base.format(args.pricelist_id);
    };
    PriceListItem.getListUrl = function (args) {
        return WMConfig.url.misconfig.api_pricelist_item_list_base.format(args.pricelist_id);
    };
    return PriceListItem;
}])
;