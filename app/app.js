// 1. 定义一个自调用的表达式函数，参数为 nx
(function(nx){

  // 2. 实例化一个 nx.ui.Application() 类，并赋值给一个变量 app
  var app = new nx.ui.Application();

  // 8. 给 nx.graphic.Topology.Link Class 自定义 2 个属性
    nx.define('CustomLinkClass', nx.graphic.Topology.Link, {
        properties: {
            sourcelabel: null,
            targetlabel: null
        },
        view: function(view) {
            view.content.push({
                name: 'source',
                type: 'nx.graphic.Text',
                props: {
                    'class': 'sourcelabel',
                    'alignment-baseline': 'text-after-edge',
                    'text-anchor': 'start'
                }
            }, {
                name: 'target',
                type: 'nx.graphic.Text',
                props: {
                    'class': 'targetlabel',
                    'alignment-baseline': 'text-after-edge',
                    'text-anchor': 'end'
                }
            });

            return view;
        },
        methods: {
            update: function() {

                this.inherited();


                var el, point;

                var line = this.line();
                var angle = line.angle();
                var stageScale = this.stageScale();

                // pad line
                line = line.pad(18 * stageScale, 18 * stageScale);

                if (this.sourcelabel()) {
                    el = this.view('source');
                    point = line.start;
                    el.set('x', point.x);
                    el.set('y', point.y);
                    el.set('text', this.sourcelabel());
                    el.set('transform', 'rotate(' + angle + ' ' + point.x + ',' + point.y + ')');
                    el.setStyle('font-size', 12 * stageScale);
                }


                if (this.targetlabel()) {
                    el = this.view('target');
                    point = line.end;
                    el.set('x', point.x);
                    el.set('y', point.y);
                    el.set('text', this.targetlabel());
                    el.set('transform', 'rotate(' + angle + ' ' + point.x + ',' + point.y + ')');
                    el.setStyle('font-size', 12 * stageScale);
                }
            }
        }
    });

  // 3. 定义一个拓扑配置文件并赋值给一个变量 topologyConfig
  var topologyConfig = {

    width: 1200,
    height: 900,
    // 指定 nodes 的配置，以 name 作为标签显示在拓扑上，图标是 “router”
    nodeConfig: {
      label: "model.mgmt_ip",
      iconType: "switch"
    },
    // 指定 links 的配置
    linkConfig: {
      linkType: "curve",
      sourcelabel: "model.srcIfName",
      targetlabel: "model.tgtIfName"
    },
    // 调用自定义的扩展 Class
    linkInstanceClass: 'CustomLinkClass',
    // true 则显示图标，false 则显示一个点。注意 t 和 f 是小写的，与 Python 不同
    showIcon: true,
    // 自动计算节点的位置，不需要指定 x 和 y 坐标
    dataProcessor: "force"

  };

  // 4. 利用第 3 步的变量 topologyConfig，实例化一个 nx.graphic.Topology() 类，并赋值给变量 topology
  var topology = new nx.graphic.Topology(topologyConfig);

  // 5. 变量 topology 从 data.js 中加载拓扑数据（topology 本身是一个 instance）
  topology.data(topologyData);

  // 6. 将 NeXt 应用实例（变量 app）绑定到拓扑实例（变量 topology）
  topology.attach(app);

  // 7. 指定 NeXt 应用实例（变量 app）运行在一个 BOM container。ID 是可以自定义的
  app.container(document.getElementById("topology-container"));

})(nx);