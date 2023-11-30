
using System;
using System.Collections.Generic;
using System.Data;
using System.Data.Common;
using System.Runtime.Serialization;
using TDSService.BaseClassLibrary;

namespace TDSService.SAL01BusinessEntities.CP.JF;

[DataContract(Namespace = "http://TDSService.DataContracts/2007/08", Name = "AakRebateApplicationCRep")]
public class AakRebateApplicationCRep : DataAccessBase<AakRebateApplicationC>
{
    public AakRebateApplicationCRep(Session session)
        : base(session)
    {
    }

    protected override void BuildMapping()
    {
        base.ORMappingVar.TableMapping("salb409C");
        base.ORMappingVar.AddColumnMapping("Id", "Id", true, "s_salb409");
        base.ORMappingVar.AddColumnMapping("DTstamp", "DTstamp");
        base.ORMappingVar.AddColumnMapping("DOperatordate", "DOperatordate");
        base.ORMappingVar.AddColumnMapping("NKaid", "NKaid");
        base.ORMappingVar.AddColumnMapping("NDealerid", "NDealerid");
        base.ORMappingVar.AddColumnMapping("NCompanyid", "NCompanyid");
        base.ORMappingVar.AddColumnMapping("NOperatorid", "NOperatorid");
        base.ORMappingVar.AddColumnMapping("NCompanyrebatemvalue", "NCompanyrebatemvalue");
        base.ORMappingVar.AddColumnMapping("NRebatemamt", "NRebatemamt");
        base.ORMappingVar.AddColumnMapping("NRebatemvalue", "NRebatemvalue");
        base.ORMappingVar.AddColumnMapping("VCompanyremark", "VCompanyremark");
        base.ORMappingVar.AddColumnMapping("VBillno", "VBillno");
        base.ORMappingVar.AddColumnMapping("VAuditinglevel", "VAuditinglevel");
        base.ORMappingVar.AddColumnMapping("VManagersuggestion", "VManagersuggestion");
        base.ORMappingVar.AddColumnMapping("VMinistersuggestion", "VMinistersuggestion");
        base.ORMappingVar.AddColumnMapping("VRebatemethod", "VRebatemethod");
        base.ORMappingVar.AddColumnMapping("VOrgremark", "VOrgremark");
        base.ORMappingVar.AddColumnMapping("VDealerremark", "VDealerremark");
        base.ORMappingVar.AddColumnMapping("VFinishstate", "VFinishstate");
        base.ORMappingVar.AddColumnMapping("VGeneralsuggestion", "VGeneralsuggestion");
        base.ORMappingVar.AddColumnMapping("VAssistantsuggestion", "VAssistantsuggestion");
        base.ORMappingVar.AddColumnMapping("NSdcaudit", "NSdcaudit");
        base.ORMappingVar.AddColumnMapping("NDkhywyaudit", "NDkhywyaudit");
        base.ORMappingVar.AddColumnMapping("NKfsjlaudit", "NKfsjlaudit");
        base.ORMappingVar.AddColumnMapping("NChsjlaudit", "NChsjlaudit");
        base.ORMappingVar.AddColumnMapping("NBzaudit", "NBzaudit");
        base.ORMappingVar.AddColumnMapping("DSdcauditdate", "DSdcauditdate");
        base.ORMappingVar.AddColumnMapping("DDkhywyauditdate", "DDkhywyauditdate");
        base.ORMappingVar.AddColumnMapping("DKfsjlauditdate", "DKfsjlauditdate");
        base.ORMappingVar.AddColumnMapping("DChsjlauditdate", "DChsjlauditdate");
        base.ORMappingVar.AddColumnMapping("DBzauditdate", "DBzauditdate");
        base.ORMappingVar.AddColumnMapping(false, "VFinishDesc", "VFinishDesc");
        base.ORMappingVar.AddColumnMapping(false, "VOperatorCode", "VOperatorCode");
        base.ORMappingVar.AddColumnMapping(false, "VOperatorName", "VOperatorName");
        base.ORMappingVar.AddColumnMapping(false, "VDealer", "VDealer");
        base.ORMappingVar.AddColumnMapping(false, "VDealerText", "VDealerText");
        base.ORMappingVar.AddColumnMapping(false, "VKacode", "VKacode");
        base.ORMappingVar.AddColumnMapping(false, "VKaname", "VKaname");
        base.ORMappingVar.AddColumnMapping(false, "VAuditinglevelcode", "VAuditinglevelcode");
        base.ORMappingVar.AddColumnMapping(false, "VGrade", "VGrade");
        base.ORMappingVar.AddColumnMapping(false, "VRebatemethodcode", "VRebatemethodcode");
        base.ORMappingVar.AddColumnMapping(false, "Vkalevel", "Vkalevel");
        base.ORMappingVar.AddColumnMapping(false, "VKalevelcode", "VKalevelcode");
        base.ORMappingVar.AddColumnMapping(false, "VOrgantext", "VOrgantext");
        base.ORMappingVar.AddColumnMapping(false, "Vtext1", "Vtext1");
        base.ORMappingVar.AddColumnMapping(false, "Vtext2", "Vtext2");
        base.ORMappingVar.AddColumnMapping(false, "Vtext3", "Vtext3");
        base.ORMappingVar.AddColumnMapping(false, "Vtext4", "Vtext4");
        base.ORMappingVar.AddColumnMapping(false, "Vtext5", "Vtext5");
        base.ORMappingVar.AddColumnMapping(false, "VTextcode1", "VTextcode1");
        base.ORMappingVar.AddColumnMapping(false, "VTextcode2", "VTextcode2");
        base.ORMappingVar.AddColumnMapping(false, "VTextcode3", "VTextcode3");
        base.ORMappingVar.AddColumnMapping(false, "VTextcode4", "VTextcode4");
        base.ORMappingVar.AddColumnMapping(false, "VTextcode5", "VTextcode5");
        base.ORMappingVar.QuerySQL = "\r\nselect a.* from salb409c a\r\n";
    }

    public override AakRebateApplicationC NewBusinessEntity()
    {
        return new AakRebateApplicationC();
    }

    public List<AakRebateApplicationC> GetAakRebateApplicationCList(string vFlag, string vFinishstate, string dOperatorBegin, string dOperatorEnd, decimal nOrgid)
    {
        return base.FindMany("p_sal91_search_salb409c", new object[11]
        {
            vFlag,
            vFinishstate,
            dOperatorBegin,
            dOperatorEnd,
            nOrgid,
            ((BaseClass)this).GetCompanyId(),
            ((BaseClass)this).GetOperatorId(),
            ((BaseClass)this).GetLanguageCode(),
            0,
            "prm_msg",
            "out_cursor"
        });
    }

    public bool DealAakRebateApplicationC(AakRebateApplicationC beInfo, string vNewstatus, string vOldstatus)
    {
        DbCommand storedProcCommand = base.DB.GetStoredProcCommand("p_sal91_update_salb409c");
        base.DB.AddInParameter(storedProcCommand, "p_docid", DbType.Decimal, (object)beInfo.Id);
        base.DB.AddInParameter(storedProcCommand, "n_operator", DbType.Decimal, (object)((BaseClass)this).GetOperatorId());
        base.DB.AddInParameter(storedProcCommand, "n_companyid", DbType.Decimal, (object)((BaseClass)this).GetCompanyId());
        base.DB.AddInParameter(storedProcCommand, "v_language", DbType.String, (object)((BaseClass)this).GetLanguageCode());
        base.DB.AddInParameter(storedProcCommand, "v_Oldstatus", DbType.String, (object)vOldstatus);
        base.DB.AddInParameter(storedProcCommand, "v_Newstatus", DbType.String, (object)vNewstatus);
        base.DB.AddOutParameter(storedProcCommand, "prm_code", DbType.Decimal, 0);
        base.DB.AddOutParameter(storedProcCommand, "prm_msg", DbType.String, 65535);
        base.DB.ExecuteNonQuery(storedProcCommand);
        int result = 0;
        if (base.DB.GetParameterValue(storedProcCommand, "prm_code") != null && !string.IsNullOrEmpty(base.DB.GetParameterValue(storedProcCommand, "prm_code").ToString()))
        {
            int.TryParse(base.DB.GetParameterValue(storedProcCommand, "prm_code").ToString(), out result);
        }
        string text = string.Empty;
        if (base.DB.GetParameterValue(storedProcCommand, "prm_msg") != null && !string.IsNullOrEmpty(base.DB.GetParameterValue(storedProcCommand, "prm_msg").ToString()))
        {
            text = base.DB.GetParameterValue(storedProcCommand, "prm_msg").ToString();
        }
        if (result != 0)
        {
            ((BaseClass)this).ThrowWarning(result, PublicFun.StringToArry(text));
            return false;
        }
        return true;
    }

    public List<AakRebateApplicationC> GetAakRebateApplicationCById(decimal nId)
    {
        base.ORMappingVar.QuerySQL = "\r\n      select a.*,\r\n             b.vdealer vDealer,\r\n             c.vlongtext   VDealerText,\r\n             d.vcode   VOperatorCode,\r\n             d.vtext   VOperatorName,\r\n             e.vtext   VFinishDesc,\r\n             f.vkacode,\r\n             f.vkaname,\r\n             g.vtext vkalevel,\r\n             h.vtext VRebatemethodcode,\r\n             f.vgrade,\r\n             i.vtext VAuditinglevelcode,\r\n             a3.vtext vOrgantext,\r\n             i2.vtext vtext1,\r\n             i2.vcode VTextcode5,\r\n             j.vtext vtext2,\r\n             k.vtext vtext3,\r\n             l.vtext vtext4,\r\n             m.vtext vtext5,\r\n             j.vcode VTextcode1,\r\n             k.vcode VTextcode2,\r\n             l.vcode VTextcode3,\r\n             m.vcode VTextcode4\r\n        from salb409c a\r\n        left join mdac100 b\r\n          on a.ndealerid = b.id\r\n        left join sysc000_m c\r\n          on b.id = c.nmainid\r\n         and c.vlanguagecode = '#0#'\r\n        left join sysc000_m d\r\n          on a.noperatorid = d.nmainid\r\n         and d.vlanguagecode = '#0#'\r\n        left join v_sysc009d e\r\n          on a.vfinishstate = e.vitemcode\r\n         and e.vdictcode = 'KAREBATESTATUS'\r\n         and e.ncompanyid = #1#\r\n        left join salb405c f\r\n        on a.nkaid=f.id\r\n        left join v_sysc009d g\r\n        on f.vkalevel=g.vitemcode\r\n        and g.vdictcode='SPCUSLEVEL'\r\n        and g.ncompanyid = #1#\r\n        left join v_sysc009d h\r\n        on a.vrebatemethod=h.vitemcode\r\n        and h.vdictcode='REBATEVALUEMETHOD'\r\n        and h.ncompanyid=#1#\r\n        left join v_sysc009d i\r\n        on a.vauditinglevel = i.vitemcode\r\n        and i.vdictcode = 'KAAUDITLEVEL'\r\n        and i.ncompanyid = #1#\r\n         left join v_dlr_sal a2 on a.ndealerid=a2.id\r\n         left join sysc000_m a3 on a2.NORGAN=a3.nmainid and a3.vlanguagecode='#0#'\r\n         left join sysc000_m i2 on a.nsdcaudit=i2.nmainid and i2.vlanguagecode='#0#'\r\n         left join sysc000_m j on a.ndkhywyaudit=j.nmainid and j.vlanguagecode='#0#'\r\n         left join sysc000_m k on a.nkfsjlaudit =k.nmainid and k.vlanguagecode='#0#'\r\n         left join sysc000_m l on a.nchsjlaudit =l.nmainid and l.vlanguagecode='#0#'\r\n         left join sysc000_m m on a.nbzaudit=m.nmainid and m.vlanguagecode='#0#' \r\n     where a.ncompanyid=#1# and a.id='#2#'and a.vfinishstate not in(90,99) \r\n";
        string[] querySqlParams = new string[3]
        {
            ((BaseClass)this).GetLanguageCode(),
            ((BaseClass)this).GetCompanyId().ToString(),
            Convert.ToString(nId)
        };
        base.ORMappingVar.SetQuerySqlParams(querySqlParams);
        return base.FindMany("");
    }
}