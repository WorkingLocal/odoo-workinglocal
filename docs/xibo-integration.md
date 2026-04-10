# Xibo CMS — Odoo Integratie

## Hoe het werkt

Odoo exposeert een publiek JSON endpoint dat Xibo ophaalt via een DataSet connector:

```
GET https://odoo.workinglocal.be/api/workspaces/availability
```

### Voorbeeldrespons

```json
{
  "updated_at": "2026-04-10T10:00:00",
  "workspaces": [
    {
      "id": 1,
      "name": "Hot Desk Zone",
      "type": "hot_desk",
      "capacity": 12,
      "is_occupied": true,
      "booked": 8,
      "available": 4,
      "next_reservation": null
    },
    {
      "id": 3,
      "name": "Vergaderzaal",
      "type": "meeting_room",
      "capacity": 8,
      "is_occupied": false,
      "booked": 0,
      "available": 8,
      "next_reservation": "2026-04-10T14:00:00"
    }
  ]
}
```

## Xibo instellen

### Stap 1 — DataSet aanmaken

1. Ga naar **DataSets** in Xibo CMS
2. **Nieuw DataSet** → kies "Remote DataSet"
3. URL: `https://odoo.workinglocal.be/api/workspaces/availability`
4. Refresh interval: 60 seconden
5. Definieer kolommen: `name`, `type`, `available`, `capacity`, `is_occupied`
6. Data path: `workspaces`

### Stap 2 — Layout aanmaken

1. Maak een nieuwe Layout (bv. 1920×1080)
2. Voeg een **DataSet View** widget toe
3. Koppel aan het WorkingLocal DataSet
4. Stijl naar wens (beschikbare CSS in `metrics-workinglocal` repo)

### Stap 3 — API key instellen (optioneel)

In Odoo: **Instellingen → Technisch → Parameters**
- Sleutel: `coworking.xibo_api_key`
- Waarde: een willekeurige geheime string

Xibo URL wordt dan:
`https://odoo.workinglocal.be/api/workspaces/availability?key=<jouw-key>`
