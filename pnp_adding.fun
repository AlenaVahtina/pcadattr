#Добавляет PNP в SMD компоненты


def pnp_adding(self):
    pads = findPath(self.fdata,["library","padStyleDef"])
    patdef = findPath(self.fdata,["library","patternDefExtended"])
    pats = findPath(self.fdata,["pcbDesign","multiLayer","pattern"])
    
    for xx in patdef:
        b = findPath(xx,["patternGraphicsDef","multiLayer","pad"])
        spads = 0
        dpads = 0
        xmaxl = 0.0
        xmaxr = 0.0
        ymaxb = 0.0
        ymaxt = 0.0
        for p in b:
            pt = find(p,"pt")
            c = find(p,"padStyleRef")[1]
            dd = find(pads,'padStyleDef',c)
    
            x=mfloat(pt[1])
            y=mfloat(pt[2])
            if mfloat(find(dd,'holeDiam')[1]):
                dpads+=1
            else:
                spads+=1
            self.logger.info('SMALL_LOG')
            shape = find(dd, 'padShape',['layerNumRef', '1'])
            dx=mfloat(find(shape,"shapeWidth")[1])/2;
            dy=mfloat(find(shape,"shapeHeight")[1])/2;
            if (spads+dpads) == 1 :
                xmaxl=x-dx
                xmaxr=x+dx
                ymaxb=y-dy
                ymaxt=y+dy
            else:
                if xmaxl>x-dx:
                    xmaxl=x-dx
                if xmaxr<x+dx:
                    xmaxr=x+dx
                if ymaxb>y-dy:
                    ymaxb=y-dy
                if ymaxt<y+dy:
                    ymaxt=y+dy
        if spads>1 and spads+dpads>0 :
            pickpoint = ['pickpoint',['pt', str((xmaxl+xmaxr)/2), str((ymaxt+ymaxb)/2)]]
            mltl = findPath(xx,["patternGraphicsDef","multiLayer"])[0]
            if findAll(mltl,'pickpoint') == []:
                mltl.append(pickpoint)
    
